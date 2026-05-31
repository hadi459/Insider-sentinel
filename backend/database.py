"""
Insider Sentinel - SQLite Database Layer
Manages schema creation, CRUD operations, and connection lifecycle.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

# Resolve database path relative to this file's directory
_DB_DIR = Path(__file__).parent.parent / "database"
_DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = _DB_DIR / "insider_sentinel.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,
    role        TEXT    NOT NULL CHECK(role IN ('admin','employee')),
    department  TEXT    DEFAULT '',
    job_title   TEXT    DEFAULT '',
    is_active   INTEGER NOT NULL DEFAULT 1,
    is_blocked  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS activity_logs (
    log_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(user_id),
    activity_type TEXT    NOT NULL,
    description   TEXT    DEFAULT '',
    timestamp     TEXT    NOT NULL DEFAULT (datetime('now')),
    ip_address    TEXT    DEFAULT '',
    metadata      TEXT    DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS risk_scores (
    score_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id       INTEGER NOT NULL REFERENCES users(user_id),
    overall_score     REAL    NOT NULL DEFAULT 0.0,
    phishing_score    REAL    NOT NULL DEFAULT 0.0,
    off_hours_score   REAL    NOT NULL DEFAULT 0.0,
    privilege_score   REAL    NOT NULL DEFAULT 0.0,
    access_score      REAL    NOT NULL DEFAULT 0.0,
    failed_login_score REAL   NOT NULL DEFAULT 0.0,
    frequency_score   REAL    NOT NULL DEFAULT 0.0,
    calculated_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id  TEXT    PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(user_id),
    token       TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at  TEXT    NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_type ON activity_logs(activity_type);
CREATE INDEX IF NOT EXISTS idx_activity_ts   ON activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_risk_employee ON risk_scores(employee_id);
CREATE INDEX IF NOT EXISTS idx_session_user  ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_session_token ON sessions(token);
"""


class Database:
    """Singleton-like database manager for SQLite operations."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self._db_path = db_path or DB_PATH
        self._initialize()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _initialize(self) -> None:
        """Create schema if not present."""
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict]:
        return dict(row) if row else None

    @staticmethod
    def _rows_to_list(rows: List[sqlite3.Row]) -> List[Dict]:
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # User CRUD
    # ------------------------------------------------------------------

    def create_user(
        self,
        name: str,
        email: str,
        password: str,
        role: str,
        department: str = "",
        job_title: str = "",
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO users (name, email, password, role, department, job_title)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, email.lower().strip(), password, role, department, job_title),
            )
            return cursor.lastrowid  # type: ignore[return-value]

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
            ).fetchone()
        return self._row_to_dict(row)

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return self._row_to_dict(row)

    def get_all_employees(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM users WHERE role = 'employee' ORDER BY name"
            ).fetchall()
        return self._rows_to_list(rows)

    def get_all_users(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
        return self._rows_to_list(rows)

    def update_user_status(self, user_id: int, is_blocked: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET is_blocked = ? WHERE user_id = ?",
                (1 if is_blocked else 0, user_id),
            )

    def update_user_active(self, user_id: int, is_active: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET is_active = ? WHERE user_id = ?",
                (1 if is_active else 0, user_id),
            )

    def count_employees(self) -> int:
        with self._connect() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'employee'"
            ).fetchone()[0]

    def count_high_risk(self, threshold: float = 0.5) -> int:
        with self._connect() as conn:
            return conn.execute(
                """SELECT COUNT(DISTINCT rs.employee_id)
                   FROM risk_scores rs
                   JOIN (
                       SELECT employee_id, MAX(calculated_at) AS latest
                       FROM risk_scores GROUP BY employee_id
                   ) latest ON rs.employee_id = latest.employee_id
                     AND rs.calculated_at = latest.latest
                   WHERE rs.overall_score >= ?""",
                (threshold,),
            ).fetchone()[0]

    # ------------------------------------------------------------------
    # Activity Log CRUD
    # ------------------------------------------------------------------

    def log_activity(
        self,
        user_id: int,
        activity_type: str,
        description: str = "",
        ip_address: str = "",
        metadata: str = "{}",
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO activity_logs
                   (user_id, activity_type, description, ip_address, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, activity_type, description, ip_address, metadata),
            )
            return cursor.lastrowid  # type: ignore[return-value]

    def get_activities_for_user(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        activity_type: Optional[str] = None,
    ) -> List[Dict]:
        with self._connect() as conn:
            if activity_type:
                rows = conn.execute(
                    """SELECT * FROM activity_logs
                       WHERE user_id = ? AND activity_type = ?
                       ORDER BY timestamp DESC LIMIT ? OFFSET ?""",
                    (user_id, activity_type, limit, offset),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM activity_logs
                       WHERE user_id = ?
                       ORDER BY timestamp DESC LIMIT ? OFFSET ?""",
                    (user_id, limit, offset),
                ).fetchall()
        return self._rows_to_list(rows)

    def get_recent_activities(self, limit: int = 100) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT al.*, u.name as user_name, u.role
                   FROM activity_logs al
                   JOIN users u ON al.user_id = u.user_id
                   ORDER BY al.timestamp DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return self._rows_to_list(rows)

    def get_activity_count_by_type(self, user_id: int) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT activity_type, COUNT(*) as count
                   FROM activity_logs WHERE user_id = ?
                   GROUP BY activity_type""",
                (user_id,),
            ).fetchall()
        return self._rows_to_list(rows)

    def get_activities_in_range(
        self, start_date: str, end_date: str
    ) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT al.*, u.name as user_name, u.department
                   FROM activity_logs al
                   JOIN users u ON al.user_id = u.user_id
                   WHERE al.timestamp BETWEEN ? AND ?
                   ORDER BY al.timestamp DESC""",
                (start_date, end_date),
            ).fetchall()
        return self._rows_to_list(rows)

    def get_link_clicks_for_user(self, user_id: int) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM activity_logs
                   WHERE user_id = ? AND activity_type = 'link_clicked'
                   ORDER BY timestamp DESC""",
                (user_id,),
            ).fetchall()
        return self._rows_to_list(rows)

    # ------------------------------------------------------------------
    # Risk Score CRUD
    # ------------------------------------------------------------------

    def upsert_risk_score(
        self,
        employee_id: int,
        overall_score: float,
        phishing_score: float,
        off_hours_score: float,
        privilege_score: float,
        access_score: float,
        failed_login_score: float,
        frequency_score: float,
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO risk_scores
                   (employee_id, overall_score, phishing_score, off_hours_score,
                    privilege_score, access_score, failed_login_score, frequency_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    employee_id,
                    overall_score,
                    phishing_score,
                    off_hours_score,
                    privilege_score,
                    access_score,
                    failed_login_score,
                    frequency_score,
                ),
            )
            # Update cached score on user row
            conn.execute(
                "UPDATE users SET is_active = is_active WHERE user_id = ?",
                (employee_id,),
            )
            return cursor.lastrowid  # type: ignore[return-value]

    def get_latest_risk_score(self, employee_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT * FROM risk_scores WHERE employee_id = ?
                   ORDER BY calculated_at DESC LIMIT 1""",
                (employee_id,),
            ).fetchone()
        return self._row_to_dict(row)

    def get_risk_history(self, employee_id: int, limit: int = 30) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM risk_scores WHERE employee_id = ?
                   ORDER BY calculated_at DESC LIMIT ?""",
                (employee_id, limit),
            ).fetchall()
        return self._rows_to_list(rows)

    def get_all_latest_risk_scores(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT rs.*
                   FROM risk_scores rs
                   JOIN (
                       SELECT employee_id, MAX(calculated_at) AS latest
                       FROM risk_scores GROUP BY employee_id
                   ) latest ON rs.employee_id = latest.employee_id
                     AND rs.calculated_at = latest.latest""",
            ).fetchall()
        return self._rows_to_list(rows)

    # ------------------------------------------------------------------
    # Session CRUD
    # ------------------------------------------------------------------

    def create_session(
        self,
        session_id: str,
        user_id: int,
        token: str,
        expires_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO sessions (session_id, user_id, token, expires_at)
                   VALUES (?, ?, ?, ?)""",
                (session_id, user_id, token, expires_at),
            )

    def get_session_by_token(self, token: str) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE token = ? AND is_active = 1",
                (token,),
            ).fetchone()
        return self._row_to_dict(row)

    def invalidate_session(self, token: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET is_active = 0 WHERE token = ?", (token,)
            )

    def invalidate_all_user_sessions(self, user_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE sessions SET is_active = 0 WHERE user_id = ?", (user_id,)
            )

    def count_active_sessions(self) -> int:
        with self._connect() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE is_active = 1"
            ).fetchone()[0]

    def get_active_sessions(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT s.*, u.name, u.email, u.role
                   FROM sessions s JOIN users u ON s.user_id = u.user_id
                   WHERE s.is_active = 1 ORDER BY s.created_at DESC""",
            ).fetchall()
        return self._rows_to_list(rows)

    # ------------------------------------------------------------------
    # Reporting helpers
    # ------------------------------------------------------------------

    def get_department_stats(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT u.department,
                          COUNT(u.user_id)        as employee_count,
                          AVG(rs.overall_score)   as avg_risk_score,
                          MAX(rs.overall_score)   as max_risk_score
                   FROM users u
                   LEFT JOIN risk_scores rs ON u.user_id = rs.employee_id
                   WHERE u.role = 'employee'
                   GROUP BY u.department""",
            ).fetchall()
        return self._rows_to_list(rows)

    def user_exists(self, email: str) -> bool:
        with self._connect() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM users WHERE email = ?", (email.lower().strip(),)
            ).fetchone()[0]
        return count > 0
