"""
Insider Sentinel - Monitoring System (Central Controller)
Coordinates authentication, activity logging, risk analysis, and admin actions.
"""
from __future__ import annotations

import json
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.database import Database
from backend.models import (
    ActivityType,
    Admin,
    Employee,
    RiskLevel,
    UserRole,
)
from backend.risk_analyzer import RiskAnalyzer


def _generate_token(length: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class MonitoringSystem:
    """Central controller that integrates auth, logging, risk calculation, and admin ops."""

    SESSION_TTL_HOURS = 8

    def __init__(self, db: Optional[Database] = None) -> None:
        self._db = db or Database()
        self._risk_analyzer = RiskAnalyzer(self._db)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self, email: str, password: str) -> Dict:
        """Authenticate a user and return session info or raise on failure."""
        user = self._db.get_user_by_email(email.lower().strip())
        if not user:
            raise ValueError("Invalid email or password")

        from backend.models import User
        if not User.verify_password(password, user["password"]):
            # Log failed login if we can identify the user
            self._db.log_activity(
                user_id=user["user_id"],
                activity_type=ActivityType.FAILED_LOGIN.value,
                description="Failed login attempt",
            )
            raise ValueError("Invalid email or password")

        if user["is_blocked"]:
            raise PermissionError("Account is blocked. Contact an administrator.")

        token = _generate_token()
        session_id = _generate_token(32)
        expires_at = (
            datetime.utcnow() + timedelta(hours=self.SESSION_TTL_HOURS)
        ).isoformat()

        self._db.create_session(
            session_id=session_id,
            user_id=user["user_id"],
            token=token,
            expires_at=expires_at,
        )

        self._db.log_activity(
            user_id=user["user_id"],
            activity_type=ActivityType.LOGIN.value,
            description=f"User logged in",
        )

        return {
            "token": token,
            "session_id": session_id,
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "expires_at": expires_at,
        }

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a bearer token and return user info, or None if invalid."""
        session = self._db.get_session_by_token(token)
        if not session:
            return None
        # Check expiry
        try:
            expires_at = datetime.fromisoformat(session["expires_at"])
        except (ValueError, TypeError):
            return None
        if datetime.utcnow() > expires_at:
            self._db.invalidate_session(token)
            return None

        user = self._db.get_user_by_id(session["user_id"])
        if not user or user["is_blocked"]:
            return None
        return user

    def logout(self, token: str) -> None:
        """Invalidate a session token."""
        session = self._db.get_session_by_token(token)
        if session:
            self._db.log_activity(
                user_id=session["user_id"],
                activity_type=ActivityType.LOGOUT.value,
                description="User logged out",
            )
            self._db.invalidate_session(token)

    # ------------------------------------------------------------------
    # Activity Logging
    # ------------------------------------------------------------------

    def log_activity(
        self,
        user_id: int,
        activity_type: str,
        description: str = "",
        ip_address: str = "",
        metadata: Optional[Dict] = None,
    ) -> int:
        meta_str = json.dumps(metadata or {})
        log_id = self._db.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            metadata=meta_str,
        )
        # Recalculate risk after each new activity (async would be better in prod)
        try:
            user = self._db.get_user_by_id(user_id)
            if user and user["role"] == "employee":
                self._risk_analyzer.calculate_risk(user_id)
        except Exception:
            pass  # Never let risk calculation crash the log call
        return log_id

    # ------------------------------------------------------------------
    # Admin Actions
    # ------------------------------------------------------------------

    def block_employee(self, admin_id: int, employee_id: int) -> None:
        self._db.update_user_status(employee_id, is_blocked=True)
        self._db.log_activity(
            user_id=admin_id,
            activity_type=ActivityType.ACCOUNT_BLOCKED.value,
            description=f"Admin blocked employee {employee_id}",
            metadata=json.dumps({"target_user_id": employee_id}),
        )
        # Also force-logout the blocked employee
        self._db.invalidate_all_user_sessions(employee_id)

    def unblock_employee(self, admin_id: int, employee_id: int) -> None:
        self._db.update_user_status(employee_id, is_blocked=False)
        self._db.log_activity(
            user_id=admin_id,
            activity_type=ActivityType.ACCOUNT_UNBLOCKED.value,
            description=f"Admin unblocked employee {employee_id}",
            metadata=json.dumps({"target_user_id": employee_id}),
        )

    def force_logout(self, admin_id: int, employee_id: int) -> None:
        self._db.invalidate_all_user_sessions(employee_id)
        self._db.log_activity(
            user_id=admin_id,
            activity_type=ActivityType.FORCE_LOGOUT.value,
            description=f"Admin force-logged-out employee {employee_id}",
            metadata=json.dumps({"target_user_id": employee_id}),
        )
        self._db.log_activity(
            user_id=employee_id,
            activity_type=ActivityType.FORCE_LOGOUT.value,
            description="Session terminated by administrator",
        )

    # ------------------------------------------------------------------
    # Dashboard Data
    # ------------------------------------------------------------------

    def get_overview_stats(self) -> Dict:
        total_employees = self._db.count_employees()
        high_risk_count = self._db.count_high_risk(threshold=0.5)
        active_sessions = self._db.count_active_sessions()
        return {
            "total_employees": total_employees,
            "high_risk_count": high_risk_count,
            "active_sessions": active_sessions,
        }

    def get_all_employees_with_risk(self) -> List[Dict]:
        employees = self._db.get_all_employees()
        risk_scores = {
            r["employee_id"]: r for r in self._db.get_all_latest_risk_scores()
        }
        activities = {e["user_id"]: self._db.get_activities_for_user(e["user_id"], limit=1)
                      for e in employees}

        current_time_iso = datetime.utcnow().isoformat()
        active_sessions = self._db.get_active_sessions()
        # Ensure session is active and not expired
        active_user_ids = {
            s["user_id"] for s in active_sessions
            if s["expires_at"] > current_time_iso
        }

        result = []
        for emp in employees:
            uid = emp["user_id"]
            rs = risk_scores.get(uid, {})
            last_acts = activities.get(uid, [])
            last_activity = last_acts[0]["timestamp"] if last_acts else None

            result.append({
                "user_id": uid,
                "name": emp["name"],
                "email": emp["email"],
                "department": emp["department"],
                "job_title": emp["job_title"],
                "is_blocked": bool(emp["is_blocked"]),
                "is_logged_in": uid in active_user_ids,
                "risk_score": rs.get("overall_score", 0.0),
                "risk_level": RiskLevel.from_score(
                    rs.get("overall_score", 0.0)
                ).value,
                "last_activity": last_activity,
            })
        return result

    def get_employee_profile(self, employee_id: int) -> Optional[Dict]:
        emp = self._db.get_user_by_id(employee_id)
        if not emp or emp["role"] != "employee":
            return None

        rs = self._db.get_latest_risk_score(employee_id) or {}
        activities = self._db.get_activities_for_user(employee_id, limit=20)
        link_clicks = self._db.get_link_clicks_for_user(employee_id)
        
        current_time_iso = datetime.utcnow().isoformat()
        active_sessions = self._db.get_active_sessions()
        is_logged_in = any(s["user_id"] == employee_id and s["expires_at"] > current_time_iso for s in active_sessions)

        return {
            "user_id": employee_id,
            "name": emp["name"],
            "email": emp["email"],
            "department": emp["department"],
            "job_title": emp["job_title"],
            "is_active": bool(emp["is_active"]),
            "is_blocked": bool(emp["is_blocked"]),
            "is_logged_in": is_logged_in,
            "created_at": emp["created_at"],
            "risk_profile": {
                "overall_score": rs.get("overall_score", 0.0),
                "phishing_score": rs.get("phishing_score", 0.0),
                "off_hours_score": rs.get("off_hours_score", 0.0),
                "privilege_score": rs.get("privilege_score", 0.0),
                "access_score": rs.get("access_score", 0.0),
                "failed_login_score": rs.get("failed_login_score", 0.0),
                "frequency_score": rs.get("frequency_score", 0.0),
                "risk_level": RiskLevel.from_score(
                    rs.get("overall_score", 0.0)
                ).value,
            },
            "recent_activities": [
                self._format_activity(a) for a in activities
            ],
            "link_clicks": [
                self._format_activity(c) for c in link_clicks
            ],
        }

    def get_heatmap_data(self) -> List[Dict]:
        employees = self._db.get_all_employees()
        risk_scores = {
            r["employee_id"]: r for r in self._db.get_all_latest_risk_scores()
        }
        result = []
        for emp in employees:
            uid = emp["user_id"]
            rs = risk_scores.get(uid, {})
            result.append({
                "name": emp["name"],
                "department": emp["department"],
                "phishing": rs.get("phishing_score", 0.0),
                "off_hours": rs.get("off_hours_score", 0.0),
                "privilege": rs.get("privilege_score", 0.0),
                "access": rs.get("access_score", 0.0),
                "failed_login": rs.get("failed_login_score", 0.0),
                "frequency": rs.get("frequency_score", 0.0),
                "overall": rs.get("overall_score", 0.0),
            })
        return result

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_employee_risk_report(self, employee_id: int) -> Dict:
        profile = self.get_employee_profile(employee_id)
        if not profile:
            raise ValueError(f"Employee {employee_id} not found")
        history = self._db.get_risk_history(employee_id, limit=10)
        profile["risk_history"] = history
        return profile

    def get_department_summary(self, department: Optional[str] = None) -> Dict:
        stats = self._db.get_department_stats()
        if department:
            stats = [s for s in stats if s.get("department") == department]
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "departments": stats,
        }

    def get_daily_activity_report(
        self, start_date: Optional[str], end_date: Optional[str]
    ) -> Dict:
        start = start_date or (datetime.utcnow() - timedelta(days=7)).strftime(
            "%Y-%m-%d"
        )
        end = end_date or datetime.utcnow().strftime("%Y-%m-%d")
        activities = self._db.get_activities_in_range(
            f"{start} 00:00:00", f"{end} 23:59:59"
        )
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "start_date": start,
            "end_date": end,
            "total_activities": len(activities),
            "activities": activities,
        }

    def get_system_overview_report(self) -> Dict:
        stats = self.get_overview_stats()
        dept_stats = self._db.get_department_stats()
        recent = self._db.get_recent_activities(limit=50)
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "overview": stats,
            "department_stats": dept_stats,
            "recent_activities": recent,
        }

    # ------------------------------------------------------------------
    # Employee self-service
    # ------------------------------------------------------------------

    def get_employee_dashboard(self, user_id: int) -> Dict:
        emp = self._db.get_user_by_id(user_id)
        if not emp:
            raise ValueError("Employee not found")
        activities = self._db.get_activities_for_user(user_id, limit=10)
        rs = self._db.get_latest_risk_score(user_id) or {}
        return {
            "name": emp["name"],
            "email": emp["email"],
            "department": emp["department"],
            "job_title": emp["job_title"],
            "is_blocked": bool(emp["is_blocked"]),
            "risk_score": rs.get("overall_score", 0.0),
            "risk_level": RiskLevel.from_score(
                rs.get("overall_score", 0.0)
            ).value,
            "recent_activities": [self._format_activity(a) for a in activities],
        }

    def get_employee_activities(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        activity_type: Optional[str] = None,
    ) -> List[Dict]:
        activities = self._db.get_activities_for_user(
            user_id, limit=limit, offset=offset, activity_type=activity_type
        )
        return [self._format_activity(a) for a in activities]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_activity(a: Dict) -> Dict:
        try:
            meta = json.loads(a.get("metadata", "{}"))
        except (json.JSONDecodeError, TypeError):
            meta = {}
        return {
            "log_id": a["log_id"],
            "user_id": a["user_id"],
            "activity_type": a["activity_type"],
            "description": a["description"],
            "timestamp": a["timestamp"],
            "ip_address": a.get("ip_address", ""),
            "metadata": meta,
        }
