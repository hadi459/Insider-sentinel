from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ActivityType(str, Enum):
    LOGIN = "login"
    FILE_ACCESS = "file_access"
    POLICY_VIOLATION = "policy_violation"


class UserRole(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class User:
    user_id: int
    name: str
    email: str
    role: UserRole


@dataclass
class Admin(User):
    pass


@dataclass
class Employee(User):
    department: str


@dataclass
class ActivityLog:
    user_id: int
    activity_type: ActivityType
    timestamp: datetime


@dataclass
class RiskProfile:
    user_id: int
    risk_score: float
    risk_level: RiskLevel


@dataclass
class Dashboard:
    total_employees: int
    high_risk_count: int
    active_sessions: int


class ReportGenerator:
    def generate_summary(self, dashboard: Dashboard) -> dict:
        return {
            "total_employees": dashboard.total_employees,
            "high_risk_count": dashboard.high_risk_count,
            "active_sessions": dashboard.active_sessions,
        }
