from __future__ import annotations

from datetime import datetime, timezone

from backend.models import ActivityLog, ActivityType


class MonitoringSystem:
    def record(self, user_id: int, activity_type: ActivityType) -> ActivityLog:
        return ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            timestamp=datetime.now(timezone.utc),
        )
