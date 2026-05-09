"""
Insider Sentinel - OOP Model Definitions
Implements class hierarchy: User -> Admin/Employee, ActivityLog, RiskProfile, Dashboard, ReportGenerator
"""
from __future__ import annotations

import hashlib
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"


class ActivityType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    TASK_COMPLETE = "task_complete"
    CHAT_MESSAGE = "chat_message"
    LINK_CLICKED = "link_clicked"
    FILE_ACCESS = "file_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    FAILED_LOGIN = "failed_login"
    FORCE_LOGOUT = "force_logout"
    ACCOUNT_BLOCKED = "account_blocked"
    ACCOUNT_UNBLOCKED = "account_unblocked"
    PAGE_VIEW = "page_view"
    DATA_EXPORT = "data_export"


class RiskLevel(str, Enum):
    LOW = "low"        # 0.0 – 0.25
    MEDIUM = "medium"  # 0.25 – 0.50
    HIGH = "high"      # 0.50 – 0.75
    CRITICAL = "critical"  # 0.75 – 1.00

    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        if score < 0.25:
            return cls.LOW
        if score < 0.50:
            return cls.MEDIUM
        if score < 0.75:
            return cls.HIGH
        return cls.CRITICAL


# ---------------------------------------------------------------------------
# Base User (Abstract)
# ---------------------------------------------------------------------------

class User(ABC):
    """Abstract base class for all system users."""

    def __init__(
        self,
        user_id: int,
        name: str,
        email: str,
        role: UserRole,
        department: str = "",
        is_active: bool = True,
        is_blocked: bool = False,
        created_at: Optional[datetime] = None,
    ) -> None:
        self._user_id = user_id
        self._name = name
        self._email = email
        self._role = role
        self._department = department
        self._is_active = is_active
        self._is_blocked = is_blocked
        self._created_at = created_at or datetime.utcnow()

    # -- Properties ----------------------------------------------------------

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def department(self) -> str:
        return self._department

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        self._is_active = value

    @property
    def is_blocked(self) -> bool:
        return self._is_blocked

    @is_blocked.setter
    def is_blocked(self, value: bool) -> None:
        self._is_blocked = value

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # -- Abstract interface --------------------------------------------------

    @abstractmethod
    def get_dashboard_data(self) -> Dict:
        """Return role-specific dashboard data."""

    # -- Common helpers ------------------------------------------------------

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a PBKDF2-HMAC-SHA256 password hash with a random salt.

        Uses 260 000 iterations — compliant with NIST SP 800-132 guidance.
        Stored format: ``<hex-salt>:<hex-dk>``
        """
        salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
        return f"{salt.hex()}:{dk.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify a plaintext password against a stored PBKDF2 hash."""
        try:
            salt_hex, dk_hex = stored_hash.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(dk_hex)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
            return secrets.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> Dict:
        return {
            "user_id": self._user_id,
            "name": self._name,
            "email": self._email,
            "role": self._role.value,
            "department": self._department,
            "is_active": self._is_active,
            "is_blocked": self._is_blocked,
            "created_at": self._created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} id={self._user_id} "
            f"email={self._email} role={self._role.value}>"
        )


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

class Admin(User):
    """Administrator with elevated privileges."""

    DEFAULT_PERMISSIONS = frozenset(
        [
            "view_all_employees",
            "block_employee",
            "unblock_employee",
            "force_logout",
            "generate_reports",
            "view_risk_scores",
            "manage_sessions",
        ]
    )

    def __init__(self, *args, permissions: Optional[frozenset] = None, **kwargs) -> None:
        kwargs.setdefault("role", UserRole.ADMIN)
        super().__init__(*args, **kwargs)
        self._permissions = permissions or self.DEFAULT_PERMISSIONS

    @property
    def permissions(self) -> frozenset:
        return self._permissions

    def has_permission(self, perm: str) -> bool:
        return perm in self._permissions

    def get_dashboard_data(self) -> Dict:
        return {
            "role": UserRole.ADMIN.value,
            "name": self._name,
            "permissions": list(self._permissions),
        }

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data["permissions"] = list(self._permissions)
        return data


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------

class Employee(User):
    """Regular employee subject to monitoring."""

    def __init__(
        self,
        *args,
        job_title: str = "",
        risk_score: float = 0.0,
        risk_level: Optional[RiskLevel] = None,
        **kwargs,
    ) -> None:
        kwargs.setdefault("role", UserRole.EMPLOYEE)
        super().__init__(*args, **kwargs)
        self._job_title = job_title
        self._risk_score = max(0.0, min(1.0, risk_score))
        self._risk_level = risk_level or RiskLevel.from_score(self._risk_score)
        self._last_activity: Optional[datetime] = None

    # -- Properties ----------------------------------------------------------

    @property
    def job_title(self) -> str:
        return self._job_title

    @property
    def risk_score(self) -> float:
        return self._risk_score

    @risk_score.setter
    def risk_score(self, value: float) -> None:
        self._risk_score = max(0.0, min(1.0, value))
        self._risk_level = RiskLevel.from_score(self._risk_score)

    @property
    def risk_level(self) -> RiskLevel:
        return self._risk_level

    @property
    def last_activity(self) -> Optional[datetime]:
        return self._last_activity

    @last_activity.setter
    def last_activity(self, value: datetime) -> None:
        self._last_activity = value

    # -- Abstract implementation ---------------------------------------------

    def get_dashboard_data(self) -> Dict:
        return {
            "role": UserRole.EMPLOYEE.value,
            "name": self._name,
            "job_title": self._job_title,
            "department": self._department,
            "risk_score": self._risk_score,
            "risk_level": self._risk_level.value,
            "is_blocked": self._is_blocked,
        }

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update(
            {
                "job_title": self._job_title,
                "risk_score": self._risk_score,
                "risk_level": self._risk_level.value,
                "last_activity": (
                    self._last_activity.isoformat() if self._last_activity else None
                ),
            }
        )
        return data


# ---------------------------------------------------------------------------
# ActivityLog
# ---------------------------------------------------------------------------

@dataclass
class ActivityLog:
    """Records a single user interaction for audit and risk analysis."""

    log_id: int
    user_id: int
    activity_type: ActivityType
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: str = ""
    metadata: Dict = field(default_factory=dict)

    def is_suspicious(self) -> bool:
        """Basic suspicion flag based on activity type."""
        suspicious_types = {
            ActivityType.LINK_CLICKED,
            ActivityType.PRIVILEGE_ESCALATION,
            ActivityType.FAILED_LOGIN,
            ActivityType.DATA_EXPORT,
        }
        return self.activity_type in suspicious_types

    def to_dict(self) -> Dict:
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "activity_type": self.activity_type.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "metadata": self.metadata,
            "is_suspicious": self.is_suspicious(),
        }


# ---------------------------------------------------------------------------
# RiskProfile
# ---------------------------------------------------------------------------

@dataclass
class RiskProfile:
    """Stores and exposes the composite risk breakdown for an employee."""

    employee_id: int
    overall_score: float = 0.0
    phishing_score: float = 0.0
    off_hours_score: float = 0.0
    privilege_score: float = 0.0
    access_score: float = 0.0
    failed_login_score: float = 0.0
    frequency_score: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.from_score(self.overall_score)

    def to_dict(self) -> Dict:
        return {
            "employee_id": self.employee_id,
            "overall_score": round(self.overall_score, 4),
            "phishing_score": round(self.phishing_score, 4),
            "off_hours_score": round(self.off_hours_score, 4),
            "privilege_score": round(self.privilege_score, 4),
            "access_score": round(self.access_score, 4),
            "failed_login_score": round(self.failed_login_score, 4),
            "frequency_score": round(self.frequency_score, 4),
            "risk_level": self.risk_level.value,
            "calculated_at": self.calculated_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class Dashboard:
    """Aggregates analytics data for the admin overview."""

    def __init__(self, monitoring_system) -> None:
        self._system = monitoring_system

    def get_overview_stats(self) -> Dict:
        """Return high-level stats: total employees, high-risk count, active sessions."""
        return self._system.get_overview_stats()

    def get_employee_list(self) -> List[Dict]:
        """Return all employees with their current risk scores."""
        return self._system.get_all_employees_with_risk()

    def get_heatmap_data(self) -> List[Dict]:
        """Return risk heatmap data for visualization."""
        return self._system.get_heatmap_data()


# ---------------------------------------------------------------------------
# ReportGenerator
# ---------------------------------------------------------------------------

class ReportGenerator:
    """Generates downloadable reports from activity and risk data."""

    REPORT_TYPES = [
        "employee_risk_profile",
        "department_summary",
        "daily_activity",
        "system_overview",
    ]

    def __init__(self, monitoring_system) -> None:
        self._system = monitoring_system

    def generate(
        self,
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        employee_id: Optional[int] = None,
        department: Optional[str] = None,
    ) -> Dict:
        """Generate a report and return structured data."""
        if report_type not in self.REPORT_TYPES:
            raise ValueError(f"Unknown report type: {report_type}")

        method = getattr(self, f"_report_{report_type}", None)
        if method is None:
            raise NotImplementedError(f"Report type not implemented: {report_type}")

        return method(
            start_date=start_date,
            end_date=end_date,
            employee_id=employee_id,
            department=department,
        )

    def _report_employee_risk_profile(self, employee_id=None, **_) -> Dict:
        if not employee_id:
            raise ValueError("employee_id required for employee_risk_profile report")
        return self._system.get_employee_risk_report(employee_id)

    def _report_department_summary(self, department=None, **_) -> Dict:
        return self._system.get_department_summary(department)

    def _report_daily_activity(self, start_date=None, end_date=None, **_) -> Dict:
        return self._system.get_daily_activity_report(start_date, end_date)

    def _report_system_overview(self, **_) -> Dict:
        return self._system.get_system_overview_report()
