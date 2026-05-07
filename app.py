from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__)

EMPLOYEES = [
    {
        "user_id": 101,
        "name": "Alice Johnson",
        "email": "alice.johnson@company.com",
        "department": "Engineering",
        "risk_score": 0.21,
        "last_activity": "2026-05-07T14:10:00Z",
        "blocked": False,
    },
    {
        "user_id": 102,
        "name": "Brian Lee",
        "email": "brian.lee@company.com",
        "department": "Finance",
        "risk_score": 0.72,
        "last_activity": "2026-05-07T14:35:00Z",
        "blocked": False,
    },
    {
        "user_id": 103,
        "name": "Carla Smith",
        "email": "carla.smith@company.com",
        "department": "HR",
        "risk_score": 0.88,
        "last_activity": "2026-05-07T15:03:00Z",
        "blocked": False,
    },
]


def _active_employees() -> list[dict]:
    return [emp for emp in EMPLOYEES if not emp.get("blocked")]


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/admin")
def admin_page():
    return send_from_directory(FRONTEND_DIR, "admin.html")


@app.get("/js/<path:filename>")
def js_files(filename: str):
    return send_from_directory(FRONTEND_DIR / "js", filename)


@app.get("/css/<path:filename>")
def css_files(filename: str):
    return send_from_directory(FRONTEND_DIR / "css", filename)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.get("/admin/dashboard")
def admin_dashboard():
    emps = _active_employees()
    high_risk = [e for e in emps if e["risk_score"] >= 0.7]
    return jsonify(
        {
            "total_employees": len(emps),
            "high_risk_count": len(high_risk),
            "active_sessions": max(1, len(emps) - 1),
        }
    )


@app.get("/admin/employees")
def admin_employees():
    return jsonify({"employees": _active_employees()})


@app.get("/admin/heatmap-data")
def admin_heatmap_data():
    emps = _active_employees()
    matrix = []
    for emp in emps:
        score = emp["risk_score"]
        matrix.append([
            round(score * 100),
            round(min(100, (score + 0.08) * 100)),
            round(min(100, (score + 0.15) * 100)),
            round(max(0, (score - 0.05) * 100)),
        ])

    return jsonify({"risk_matrix": matrix})


@app.post("/admin/employee/<int:emp_id>/block")
def block_employee(emp_id: int):
    for employee in EMPLOYEES:
        if employee["user_id"] == emp_id:
            employee["blocked"] = True
            return jsonify({"success": True})
    return jsonify({"success": False, "error": "Employee not found"}), 404


@app.post("/api/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if username.lower() == "admin" and password == "admin123":
        return jsonify(
            {
                "token": "demo-admin-token",
                "user": {
                    "id": 1,
                    "name": "Admin User",
                    "email": "admin@company.com",
                    "role": "admin",
                },
            }
        )

    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes", "on"}
    app.run(host="0.0.0.0", port=5000, debug=debug)
