"""
Insider Sentinel - Behavioral Risk Analyzer
Computes weighted risk scores across six behavioral dimensions.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

from backend.models import RiskLevel, RiskProfile


class RiskFactor(str, Enum):
    PHISHING = "phishing"
    OFF_HOURS = "off_hours"
    PRIVILEGE = "privilege"
    ACCESS = "access"
    FAILED_LOGIN = "failed_login"
    FREQUENCY = "frequency"


# ---------------------------------------------------------------------------
# Weights (must sum to 1.0)
# ---------------------------------------------------------------------------
FACTOR_WEIGHTS: Dict[RiskFactor, float] = {
    RiskFactor.PHISHING: 0.30,
    RiskFactor.OFF_HOURS: 0.15,
    RiskFactor.PRIVILEGE: 0.25,
    RiskFactor.ACCESS: 0.10,
    RiskFactor.FAILED_LOGIN: 0.10,
    RiskFactor.FREQUENCY: 0.10,
}

# Off-hours window: before 8 AM or after 8 PM
OFF_HOURS_START = time(20, 0)
OFF_HOURS_END = time(8, 0)

# Thresholds
FAST_CLICK_THRESHOLD_MS = 3000        # < 3 s → very suspicious
MODERATE_CLICK_THRESHOLD_MS = 10000   # < 10 s → somewhat suspicious
MAX_FAILED_LOGINS = 5                 # normalise failed logins against this
MAX_DAILY_ACTIVITIES = 100            # normalise activity frequency against this
BULK_ACCESS_THRESHOLD = 10            # >10 file accesses → suspicious


class RiskAnalyzer:
    """Computes behavioral risk scores from activity log data."""

    def __init__(self, db) -> None:
        """
        Parameters
        ----------
        db : Database
            The database instance used to fetch activity data.
        """
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_risk(self, employee_id: int) -> RiskProfile:
        """Calculate and persist a full risk profile for an employee."""
        activities = self._db.get_activities_for_user(employee_id, limit=500)

        phishing_score = self._phishing_score(employee_id, activities)
        off_hours_score = self._off_hours_score(activities)
        privilege_score = self._privilege_score(activities)
        access_score = self._access_score(activities)
        failed_login_score = self._failed_login_score(activities)
        frequency_score = self._frequency_score(activities)

        overall_score = (
            phishing_score * FACTOR_WEIGHTS[RiskFactor.PHISHING]
            + off_hours_score * FACTOR_WEIGHTS[RiskFactor.OFF_HOURS]
            + privilege_score * FACTOR_WEIGHTS[RiskFactor.PRIVILEGE]
            + access_score * FACTOR_WEIGHTS[RiskFactor.ACCESS]
            + failed_login_score * FACTOR_WEIGHTS[RiskFactor.FAILED_LOGIN]
            + frequency_score * FACTOR_WEIGHTS[RiskFactor.FREQUENCY]
        )
        overall_score = round(min(1.0, max(0.0, overall_score)), 4)

        self._db.upsert_risk_score(
            employee_id=employee_id,
            overall_score=overall_score,
            phishing_score=round(phishing_score, 4),
            off_hours_score=round(off_hours_score, 4),
            privilege_score=round(privilege_score, 4),
            access_score=round(access_score, 4),
            failed_login_score=round(failed_login_score, 4),
            frequency_score=round(frequency_score, 4),
        )

        return RiskProfile(
            employee_id=employee_id,
            overall_score=overall_score,
            phishing_score=phishing_score,
            off_hours_score=off_hours_score,
            privilege_score=privilege_score,
            access_score=access_score,
            failed_login_score=failed_login_score,
            frequency_score=frequency_score,
        )

    def calculate_all(self, employee_ids: List[int]) -> Dict[int, RiskProfile]:
        """Calculate risk for every employee in the list."""
        return {eid: self.calculate_risk(eid) for eid in employee_ids}

    def get_risk_trend(self, employee_id: int) -> List[Dict]:
        """Return historical risk score records for trend charting."""
        history = self._db.get_risk_history(employee_id, limit=30)
        return [
            {
                "date": row["calculated_at"],
                "overall_score": row["overall_score"],
            }
            for row in history
        ]

    # ------------------------------------------------------------------
    # Per-factor scoring helpers
    # ------------------------------------------------------------------

    def _phishing_score(
        self, employee_id: int, activities: List[Dict]
    ) -> float:
        """Score based on phishing link click speed."""
        link_clicks = [
            a for a in activities if a["activity_type"] == "link_clicked"
        ]
        if not link_clicks:
            return 0.0

        scores: List[float] = []
        for click in link_clicks:
            try:
                meta = json.loads(click.get("metadata", "{}"))
            except (json.JSONDecodeError, TypeError):
                meta = {}
            response_ms = meta.get("response_time_ms", None)
            if response_ms is None:
                scores.append(0.5)  # unknown → moderate risk
            elif response_ms < FAST_CLICK_THRESHOLD_MS:
                scores.append(1.0)
            elif response_ms < MODERATE_CLICK_THRESHOLD_MS:
                scores.append(0.6)
            else:
                scores.append(0.2)

        return min(1.0, sum(scores) / max(len(scores), 1))

    def _off_hours_score(self, activities: List[Dict]) -> float:
        """Score based on fraction of activities outside business hours."""
        if not activities:
            return 0.0
        off_count = sum(
            1
            for a in activities
            if self._is_off_hours(a.get("timestamp", ""))
        )
        return min(1.0, off_count / max(len(activities), 1))

    def _privilege_score(self, activities: List[Dict]) -> float:
        """Score based on privilege escalation attempts."""
        priv_events = [
            a for a in activities if a["activity_type"] == "privilege_escalation"
        ]
        if not priv_events:
            return 0.0
        return min(1.0, len(priv_events) / 5)

    def _access_score(self, activities: List[Dict]) -> float:
        """Score based on bulk file access and data exports."""
        access_events = [
            a
            for a in activities
            if a["activity_type"] in ("file_access", "data_export")
        ]
        if not access_events:
            return 0.0
        return min(1.0, len(access_events) / BULK_ACCESS_THRESHOLD)

    def _failed_login_score(self, activities: List[Dict]) -> float:
        """Score based on failed login attempts."""
        failed = [
            a for a in activities if a["activity_type"] == "failed_login"
        ]
        if not failed:
            return 0.0
        return min(1.0, len(failed) / MAX_FAILED_LOGINS)

    def _frequency_score(self, activities: List[Dict]) -> float:
        """Score based on abnormal activity frequency in the last 24 hours."""
        if not activities:
            return 0.0
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = [
            a
            for a in activities
            if self._parse_ts(a.get("timestamp", "")) >= cutoff
        ]
        return min(1.0, len(recent) / MAX_DAILY_ACTIVITIES)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_ts(ts_str: str) -> datetime:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(ts_str, fmt)
            except (ValueError, TypeError):
                continue
        return datetime.min

    @staticmethod
    def _is_off_hours(ts_str: str) -> bool:
        ts = RiskAnalyzer._parse_ts(ts_str)
        if ts == datetime.min:
            return False
        t = ts.time()
        return t >= OFF_HOURS_START or t < OFF_HOURS_END
