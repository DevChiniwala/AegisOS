"""Root Cause Agent — Identifies why fraud occurred."""
import uuid

from core.schemas.investigation import Finding
from core.utils.helpers import utc_now

from ..base import BaseAgent, InvestigationContext


class RootCauseAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RootCauseAnalyst",
            role="Forensic Analyst",
            description="Identifies the root cause and attack vector of suspected fraud by analyzing control failures, vulnerability exploitation, and attacker methodology",
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        features = context.features
        graph_data = context.graph_data
        previous = context.previous_findings
        risk = context.risk_score
        causes = []
        confidence = 0.4

        if features.get("is_new_device", 0) == 1.0:
            causes.append("New device used — possible account takeover via credential stuffing")
            confidence += 0.15

        if features.get("geo_velocity_anomaly", 0) > 0:
            causes.append("Impossible travel detected — compromised credentials in use from multiple locations")
            confidence += 0.2

        velocity = features.get("transaction_velocity_1h", 0)
        if velocity > 5:
            causes.append(f"Automated attack pattern: {velocity} rapid-fire transactions suggest bot-driven fraud")
            confidence += 0.15

        if graph_data.get("fraud_rings"):
            causes.append("Organized fraud ring involvement — coordinated multi-account attack")
            confidence += 0.2

        amount = float(context.transaction.amount) if context.transaction.amount else 0
        if 9000 < amount < 10000:
            causes.append("Structuring pattern: amount below CTR threshold — deliberate evasion of reporting")
            confidence += 0.1

        if features.get("account_age_days", 365) < 7:
            causes.append("Newly created account — synthetic identity or account farming")
            confidence += 0.1

        high_risk_findings = [f for f in previous if f.confidence_score > 0.7]
        if len(high_risk_findings) >= 3:
            causes.append(f"Multiple high-confidence indicators ({len(high_risk_findings)}) — multi-vector attack")
            confidence += 0.1

        confidence = min(confidence, 0.99)
        desc = "; ".join(causes) if causes else "No clear root cause identified — legitimate transaction probable"

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Root Cause Analysis",
            description=desc,
            confidence_score=confidence,
            created_at=utc_now(),
        )
