"""Investigation Planner Agent — Decomposes investigations into sub-tasks."""
import uuid
from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PlannerAgent",
            role="Investigation Planner",
            description="Decomposes complex investigations into prioritized sub-tasks based on risk indicators and available evidence",
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        risk = context.risk_score
        tx = context.transaction
        plan_steps = []

        plan_steps.append("1. Verify transaction metadata and timestamps")

        if risk > 0.7:
            plan_steps.append("2. Deep entity resolution (sender + receiver)")
            plan_steps.append("3. Full graph traversal (2-hop network)")
            plan_steps.append("4. Behavioral pattern deviation analysis")
            plan_steps.append("5. Compliance screening (OFAC/PEP)")
            plan_steps.append("6. SAR narrative preparation")
        elif risk > 0.4:
            plan_steps.append("2. Entity linkage check")
            plan_steps.append("3. Graph context (1-hop)")
            plan_steps.append("4. Behavioral baseline comparison")
        else:
            plan_steps.append("2. Basic entity verification")
            plan_steps.append("3. Routine monitoring flag")

        amount = float(tx.amount) if tx.amount else 0
        if amount > 50000:
            plan_steps.append(f"PRIORITY: Large value transaction (${amount:,.2f}) — escalate timeline")
        if context.graph_data.get("fraud_rings"):
            plan_steps.append("PRIORITY: Known fraud ring association — deep investigation required")

        confidence = min(0.5 + (risk * 0.3), 0.95)

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Investigation Plan",
            description=f"Generated {len(plan_steps)}-step plan: " + "; ".join(plan_steps),
            confidence_score=confidence,
            created_at=utc_now(),
        )
