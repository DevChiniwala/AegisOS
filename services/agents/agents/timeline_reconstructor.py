"""Timeline Reconstructor Agent — Builds temporal event sequences."""
import uuid
from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now


class TimelineReconstructorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TimelineReconstructor",
            role="Temporal Analyst",
            description="Reconstructs chronological event sequences to identify velocity anomalies, time-based patterns, and suspicious temporal clustering",
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        features = context.features
        findings = []
        confidence = 0.5

        velocity_1h = features.get("transaction_velocity_1h", 0)
        velocity_24h = features.get("transaction_velocity_24h", 0)
        time_since_last = features.get("time_since_last_transaction", float("inf"))

        if velocity_1h > 5:
            findings.append(f"High-velocity burst: {velocity_1h} transactions in last hour")
            confidence += 0.2
        elif velocity_1h > 3:
            findings.append(f"Elevated activity: {velocity_1h} transactions in last hour")
            confidence += 0.1

        if velocity_24h > 20:
            findings.append(f"Unusual daily volume: {velocity_24h} transactions in 24h")
            confidence += 0.15

        if time_since_last < 60:
            findings.append(f"Rapid succession: only {time_since_last:.0f}s since last transaction")
            confidence += 0.15

        hour_of_day = features.get("hour_of_day", 12)
        if hour_of_day < 5 or hour_of_day > 23:
            findings.append(f"Off-hours activity at hour {hour_of_day}")
            confidence += 0.05

        is_weekend = features.get("is_weekend", 0)
        is_holiday = features.get("is_holiday", 0)
        if is_weekend and velocity_1h > 3:
            findings.append("Weekend burst activity")
            confidence += 0.05
        if is_holiday:
            findings.append("Holiday transaction — reduced monitoring window")
            confidence += 0.05

        confidence = min(confidence, 0.99)
        desc = "; ".join(findings) if findings else "Normal temporal patterns observed"

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Temporal Pattern Analysis",
            description=desc,
            confidence_score=confidence,
            created_at=utc_now(),
        )
