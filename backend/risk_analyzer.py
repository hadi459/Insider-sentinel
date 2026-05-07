from __future__ import annotations

from enum import Enum


class RiskFactor(str, Enum):
    LOGIN_ANOMALY = "login_anomaly"
    DATA_EXFILTRATION = "data_exfiltration"


class RiskAnalyzer:
    def calculate(self, base_score: float, factors: list[RiskFactor] | None = None) -> float:
        factors = factors or []
        adjusted = base_score + (0.1 * len(factors))
        return max(0.0, min(1.0, adjusted))
