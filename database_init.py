"""
Insider Sentinel - Database Initialization Script
Seeds 2 Admin and 8 Employee accounts with realistic sample data.
Run: python database_init.py
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from backend.database import Database
from backend.models import User
from backend.risk_analyzer import RiskAnalyzer


ADMINS = [
    {"name": "Abdul Hadi", "email": "AbdulHadi@insider.com", "department": "IT Security", "job_title": "Security Manager", "password": "Ben.64170is.com"},
]

EMPLOYEES = [
    {"name": "Irum Andleeb", "email": "IrumAndleeb@insider.com", "department": "Engineering", "job_title": "Software Engineer", "password": "Mam123"},
    {"name": "Hafsa Umer", "email": "HafsaUmer@insider.com", "department": "Finance", "job_title": "Financial Analyst", "password": "Hafsa123"},
    {"name": "Sara Shahzad", "email": "SaraShahzad@insider.com", "department": "Marketing", "job_title": "Marketing Manager", "password": "Sara123"},
]

DEFAULT_PASSWORD = "Secure@123"

ACTIVITY_TEMPLATES = [
    ("login",                "User logged in",                    {}),
    ("logout",               "User logged out",                   {}),
    ("task_complete",        "Completed task: Review Q4 report",  {"task_id": 1}),
    ("chat_message",         "Chat message sent",                 {"length": 42}),
    ("file_access",          "Accessed file: budget_2024.xlsx",   {"filename": "budget_2024.xlsx"}),
    ("page_view",            "Visited internal portal page",      {}),
    ("privilege_escalation", "Attempted privilege escalation",    {}),
    ("data_export",          "Exported employee records",         {"rows": 150}),
    ("failed_login",         "Failed login attempt",              {}),
]


def _random_ts(days_back: int = 30) -> str:
    delta = random.uniform(0, days_back * 24 * 3600)
    ts = datetime.utcnow() - timedelta(seconds=delta)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def _seed_activities(db: Database, user_id: int, count: int, include_phishing: bool = False) -> None:
    for _ in range(count):
        template = random.choice(ACTIVITY_TEMPLATES)
        atype, desc, meta = template
        ts = _random_ts()
        db._db_path  # ensure path exists
        with db._connect() as conn:
            conn.execute(
                """INSERT INTO activity_logs
                   (user_id, activity_type, description, timestamp, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, atype, desc, ts, json.dumps(meta)),
            )

    if include_phishing:
        # Seed 2-5 phishing link clicks with various response times
        for _ in range(random.randint(2, 5)):
            response_ms = random.choice([1200, 2800, 5500, 12000, 25000])
            meta = {"url": "http://suspicious-phish.xyz/click", "response_time_ms": response_ms}
            ts = _random_ts(7)
            with db._connect() as conn:
                conn.execute(
                    """INSERT INTO activity_logs
                       (user_id, activity_type, description, timestamp, metadata)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, "link_clicked", f"Phishing link clicked (response: {response_ms}ms)", ts, json.dumps(meta)),
                )


def init_database(skip_if_exists: bool = False) -> None:
    """Create schema, seed users and sample activities."""
    db = Database()

    if skip_if_exists and db.count_employees() > 0:
        print("Database already populated, skipping seed.")
        return

    print("Seeding admins...")
    for admin in ADMINS:
        if not db.user_exists(admin["email"]):
            password_hash = User.hash_password(admin.get("password", DEFAULT_PASSWORD))
            db.create_user(
                name=admin["name"],
                email=admin["email"],
                password=password_hash,
                role="admin",
                department=admin["department"],
                job_title=admin["job_title"],
            )
            print(f"  Created admin: {admin['email']}")
        else:
            print(f"  Admin already exists: {admin['email']}")

    print("Seeding employees...")
    for i, emp in enumerate(EMPLOYEES):
        if not db.user_exists(emp["email"]):
            password_hash = User.hash_password(emp.get("password", DEFAULT_PASSWORD))
            uid = db.create_user(
                name=emp["name"],
                email=emp["email"],
                password=password_hash,
                role="employee",
                department=emp["department"],
                job_title=emp["job_title"],
            )
            print(f"  Created employee: {emp['email']} (id={uid})")
            # Seed sample activities; make a few employees higher-risk
            include_phishing = i in (1, 3, 6)  # emp2, emp4, emp7 are riskier
            activity_count = random.randint(20, 60)
            _seed_activities(db, uid, activity_count, include_phishing=include_phishing)
        else:
            print(f"  Employee already exists: {emp['email']}")

    print("Calculating initial risk scores...")
    employees = db.get_all_employees()
    analyzer = RiskAnalyzer(db)
    for emp in employees:
        analyzer.calculate_risk(emp["user_id"])
        print(f"  Risk calculated for {emp['name']}")

    print("\n✅ Database initialization complete!")
    # print("   Admin logins:    admin1@insider.com  (see DEFAULT_PASSWORD in source)")
    # print("                    admin2@insider.com  (see DEFAULT_PASSWORD in source)")
    # print("   Employee logins: emp1-emp8@company.com  (see DEFAULT_PASSWORD in source)")


if __name__ == "__main__":
    init_database()
