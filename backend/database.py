from __future__ import annotations

from backend.models import Employee, UserRole


class Database:
    """Simple in-memory demo database."""

    def __init__(self) -> None:
        self.employees = [
            Employee(
                user_id=101,
                name="Alice Johnson",
                email="alice.johnson@company.com",
                role=UserRole.EMPLOYEE,
                department="Engineering",
            )
        ]

    def list_employees(self) -> list[Employee]:
        return list(self.employees)
