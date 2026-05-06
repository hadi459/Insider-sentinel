"""
Insider Sentinel - Flask API Routes
RESTful endpoints for Authentication, Admin, Employee, and System.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from functools import wraps
from typing import Callable, Dict, Optional, Tuple

from flask import Blueprint, jsonify, request, g

from backend.monitoring_system import MonitoringSystem
from backend.models import ActivityType, ReportGenerator

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blueprint & shared system instance
# ---------------------------------------------------------------------------

api = Blueprint("api", __name__, url_prefix="/api")

_system: Optional[MonitoringSystem] = None


def get_system() -> MonitoringSystem:
    global _system
    if _system is None:
        _system = MonitoringSystem()
    return _system


# ---------------------------------------------------------------------------
# Auth decorators
# ---------------------------------------------------------------------------

def _extract_token() -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return request.cookies.get("token")


def require_auth(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        user = get_system().verify_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.current_user = user
        g.token = token
        return f(*args, **kwargs)
    return wrapper


def require_admin(f: Callable) -> Callable:
    @wraps(f)
    @require_auth
    def wrapper(*args, **kwargs):
        if g.current_user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapper


def require_employee(f: Callable) -> Callable:
    @wraps(f)
    @require_auth
    def wrapper(*args, **kwargs):
        if g.current_user.get("role") != "employee":
            return jsonify({"error": "Employee access required"}), 403
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok(data: Dict, status: int = 200):
    return jsonify({"success": True, "data": data}), status


def _err(message: str, status: int = 400):
    return jsonify({"success": False, "error": message}), status


def _get_ip() -> str:
    return (
        request.headers.get("X-Forwarded-For", request.remote_addr) or ""
    ).split(",")[0].strip()


# ===========================================================================
# Auth Routes
# ===========================================================================

@api.route("/auth/login", methods=["POST"])
def auth_login():
    """POST /api/auth/login — Email-based login, returns bearer token."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return _err("Email and password are required")

    try:
        session_info = get_system().authenticate(email, password)
    except PermissionError:
        return _err("Account is suspended. Contact your administrator.", 403)
    except ValueError:
        return _err("Invalid email or password.", 401)

    return _ok(session_info)


@api.route("/auth/logout", methods=["POST"])
@require_auth
def auth_logout():
    """POST /api/auth/logout — Invalidate current session."""
    get_system().logout(g.token)
    return _ok({"message": "Logged out successfully"})


@api.route("/auth/verify", methods=["GET"])
@require_auth
def auth_verify():
    """GET /api/auth/verify — Verify token validity."""
    user = g.current_user
    return _ok({
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    })


# ===========================================================================
# Admin Routes
# ===========================================================================

@api.route("/admin/dashboard", methods=["GET"])
@require_admin
def admin_dashboard():
    """GET /api/admin/dashboard — Overview stats."""
    stats = get_system().get_overview_stats()
    return _ok(stats)


@api.route("/admin/employees", methods=["GET"])
@require_admin
def admin_employees():
    """GET /api/admin/employees — All employees with risk scores."""
    employees = get_system().get_all_employees_with_risk()
    return _ok({"employees": employees, "total": len(employees)})


@api.route("/admin/employee/<int:emp_id>", methods=["GET"])
@require_admin
def admin_employee_profile(emp_id: int):
    """GET /api/admin/employee/<id> — Full employee profile."""
    profile = get_system().get_employee_profile(emp_id)
    if not profile:
        return _err("Employee not found", 404)
    return _ok(profile)


@api.route("/admin/employee/<int:emp_id>/activities", methods=["GET"])
@require_admin
def admin_employee_activities(emp_id: int):
    """GET /api/admin/employee/<id>/activities — Paginated activity log."""
    limit = min(int(request.args.get("limit", 50)), 200)
    offset = int(request.args.get("offset", 0))
    activity_type = request.args.get("type")
    activities = get_system().get_employee_activities(
        emp_id, limit=limit, offset=offset, activity_type=activity_type
    )
    return _ok({"activities": activities, "count": len(activities)})


@api.route("/admin/employee/<int:emp_id>/risk-profile", methods=["GET"])
@require_admin
def admin_employee_risk_profile(emp_id: int):
    """GET /api/admin/employee/<id>/risk-profile — Detailed risk breakdown."""
    from backend.risk_analyzer import RiskAnalyzer
    system = get_system()
    analyzer = RiskAnalyzer(system._db)
    profile = analyzer.calculate_risk(emp_id)
    trend = analyzer.get_risk_trend(emp_id)
    return _ok({"risk_profile": profile.to_dict(), "trend": trend})


@api.route("/admin/employee/<int:emp_id>/block", methods=["POST"])
@require_admin
def admin_block_employee(emp_id: int):
    """POST /api/admin/employee/<id>/block — Block/suspend employee."""
    admin_id = g.current_user["user_id"]
    try:
        get_system().block_employee(admin_id, emp_id)
    except Exception:
        log.exception("Failed to block employee %s", emp_id)
        return _err("Failed to block employee. Please try again.")
    return _ok({"message": f"Employee {emp_id} has been blocked"})


@api.route("/admin/employee/<int:emp_id>/unblock", methods=["POST"])
@require_admin
def admin_unblock_employee(emp_id: int):
    """POST /api/admin/employee/<id>/unblock — Unblock employee."""
    admin_id = g.current_user["user_id"]
    try:
        get_system().unblock_employee(admin_id, emp_id)
    except Exception:
        return _err("Failed to unblock employee. Please try again.")
    return _ok({"message": f"Employee {emp_id} has been unblocked"})


@api.route("/admin/employee/<int:emp_id>/force-logout", methods=["POST"])
@require_admin
def admin_force_logout(emp_id: int):
    """POST /api/admin/employee/<id>/force-logout — Force-terminate sessions."""
    admin_id = g.current_user["user_id"]
    try:
        get_system().force_logout(admin_id, emp_id)
    except Exception:
        return _err("Failed to force logout. Please try again.")
    return _ok({"message": f"Employee {emp_id} sessions terminated"})


@api.route("/admin/reports", methods=["GET"])
@require_admin
def admin_reports():
    """GET /api/admin/reports — List available report types."""
    return _ok({"report_types": ReportGenerator.REPORT_TYPES})


@api.route("/admin/reports/generate", methods=["POST"])
@require_admin
def admin_reports_generate():
    """POST /api/admin/reports/generate — Generate a custom report."""
    data = request.get_json(silent=True) or {}
    report_type = data.get("report_type", "system_overview")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    employee_id = data.get("employee_id")
    department = data.get("department")

    system = get_system()
    reporter = ReportGenerator(system)
    try:
        report_data = reporter.generate(
            report_type,
            start_date=start_date,
            end_date=end_date,
            employee_id=employee_id,
            department=department,
        )
    except (ValueError, NotImplementedError):
        return _err("Invalid report type or missing required parameters.")
    return _ok({"report": report_data, "generated_at": datetime.utcnow().isoformat()})


@api.route("/admin/heatmap-data", methods=["GET"])
@require_admin
def admin_heatmap_data():
    """GET /api/admin/heatmap-data — Risk heatmap data."""
    data = get_system().get_heatmap_data()
    return _ok({"heatmap": data})


# ===========================================================================
# Employee Routes
# ===========================================================================

@api.route("/employee/dashboard", methods=["GET"])
@require_employee
def employee_dashboard():
    """GET /api/employee/dashboard — Employee's own dashboard."""
    user_id = g.current_user["user_id"]
    try:
        data = get_system().get_employee_dashboard(user_id)
    except ValueError:
        return _err("Employee not found.", 404)
    return _ok(data)


@api.route("/employee/tasks", methods=["GET"])
@require_employee
def employee_tasks():
    """GET /api/employee/tasks — Return simulated task list."""
    tasks = [
        {"task_id": 1, "title": "Review Q4 budget report", "priority": "high", "completed": False},
        {"task_id": 2, "title": "Update project documentation", "priority": "medium", "completed": False},
        {"task_id": 3, "title": "Attend security briefing", "priority": "high", "completed": False},
        {"task_id": 4, "title": "Submit timesheet", "priority": "low", "completed": False},
        {"task_id": 5, "title": "Code review for PR #42", "priority": "medium", "completed": False},
        {"task_id": 6, "title": "Schedule 1:1 with manager", "priority": "low", "completed": False},
    ]
    return _ok({"tasks": tasks})


@api.route("/employee/task/complete", methods=["POST"])
@require_employee
def employee_task_complete():
    """POST /api/employee/task/complete — Log task completion."""
    user_id = g.current_user["user_id"]
    data = request.get_json(silent=True) or {}
    task_id = data.get("task_id")
    task_title = data.get("task_title", f"Task {task_id}")

    if not task_id:
        return _err("task_id is required")

    get_system().log_activity(
        user_id=user_id,
        activity_type=ActivityType.TASK_COMPLETE.value,
        description=f"Completed task: {task_title}",
        ip_address=_get_ip(),
        metadata={"task_id": task_id, "task_title": task_title},
    )
    return _ok({"message": "Task logged", "task_id": task_id})


@api.route("/employee/chat/message", methods=["POST"])
@require_employee
def employee_chat_message():
    """POST /api/employee/chat/message — Log chat activity."""
    user_id = g.current_user["user_id"]
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    get_system().log_activity(
        user_id=user_id,
        activity_type=ActivityType.CHAT_MESSAGE.value,
        description=f"Chat message sent",
        ip_address=_get_ip(),
        metadata={"length": len(message)},
    )
    return _ok({"message": "Message logged"})


@api.route("/employee/link-clicked", methods=["POST"])
@require_employee
def employee_link_clicked():
    """POST /api/employee/link-clicked — Log phishing link click with response time."""
    user_id = g.current_user["user_id"]
    data = request.get_json(silent=True) or {}
    link_url = data.get("url", "unknown")
    response_time_ms = data.get("response_time_ms")  # milliseconds from appearance to click

    metadata: Dict = {"url": link_url}
    if response_time_ms is not None:
        try:
            metadata["response_time_ms"] = int(response_time_ms)
        except (TypeError, ValueError):
            pass

    get_system().log_activity(
        user_id=user_id,
        activity_type=ActivityType.LINK_CLICKED.value,
        description=f"Phishing link clicked: {link_url}",
        ip_address=_get_ip(),
        metadata=metadata,
    )
    return _ok({"message": "Link click logged", "response_time_ms": metadata.get("response_time_ms")})


@api.route("/employee/activity-log", methods=["GET"])
@require_employee
def employee_activity_log():
    """GET /api/employee/activity-log — Personal activity history."""
    user_id = g.current_user["user_id"]
    limit = min(int(request.args.get("limit", 50)), 200)
    offset = int(request.args.get("offset", 0))
    activity_type = request.args.get("type")

    activities = get_system().get_employee_activities(
        user_id, limit=limit, offset=offset, activity_type=activity_type
    )
    return _ok({"activities": activities, "count": len(activities)})


# ===========================================================================
# System Routes
# ===========================================================================

@api.route("/system/health", methods=["GET"])
def system_health():
    """GET /api/system/health — Liveness check."""
    return _ok({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    })


@api.route("/system/stats", methods=["GET"])
@require_auth
def system_stats():
    """GET /api/system/stats — Overall system statistics."""
    stats = get_system().get_overview_stats()
    dept = get_system()._db.get_department_stats()
    return _ok({"stats": stats, "departments": dept})
