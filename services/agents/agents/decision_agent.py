from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DecisionAgent",
            role="Adjudicator",
            description="Makes final APPROVE/DECLINE/ESCALATE decision"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        decision = "APPROVE"
        if context.risk_score > 0.8:
            decision = "DECLINE"
        elif context.risk_score > 0.5:
            decision = "ESCALATE"
            
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Final Decision",
            description=f"Decision rendered: {decision} based on composite risk score {context.risk_score}",
            confidence_score=0.95,
            created_at=utc_now()
        )
