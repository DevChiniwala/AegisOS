"""Recommendation Agent — Suggests preventive actions and controls."""
import uuid

from core.schemas.investigation import Finding
from core.utils.helpers import utc_now

from ..base import BaseAgent, InvestigationContext


class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RecommendationAgent",
            role="Controls Advisor",
            description="Suggests preventive actions, control enhancements, and remediation steps based on investigation findings",
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        risk = context.risk_score
        features = context.features
        previous = context.previous_findings
        recommendations = []

        if risk > 0.85:
            recommendations.append("IMMEDIATE: Block transaction and freeze account pending review")
            recommendations.append("File SAR within 30 days per BSA requirements")
            recommendations.append("Escalate to fraud operations team for manual investigation")

        if features.get("is_new_device", 0) == 1.0:
            recommendations.append("CONTROL: Enforce step-up authentication for unrecognized devices")

        velocity = features.get("transaction_velocity_1h", 0)
        if velocity > 5:
            recommendations.append("CONTROL: Implement velocity limits (max 5 tx/hour for this risk tier)")

        if features.get("geo_velocity_anomaly", 0) > 0:
            recommendations.append("CONTROL: Enable impossible-travel detection as hard block")

        graph_findings = [f for f in previous if "ring" in f.description.lower()]
        if graph_findings:
            recommendations.append("INVESTIGATION: Expand ring analysis to all connected accounts")
            recommendations.append("CONTROL: Flag all ring members for enhanced due diligence")

        if 0.4 < risk <= 0.85:
            recommendations.append("MONITORING: Add to enhanced monitoring watchlist for 90 days")
            recommendations.append("REVIEW: Schedule periodic account review")

        if risk <= 0.4:
            recommendations.append("No action required — continue routine monitoring")

        confidence = min(0.7 + (risk * 0.2), 0.95)
        desc = " | ".join(recommendations)

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Recommended Actions",
            description=desc,
            confidence_score=confidence,
            created_at=utc_now(),
        )
