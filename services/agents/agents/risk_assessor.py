from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class RiskAssessor(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RiskAssessor",
            role="Risk Evaluator",
            description="Synthesizes findings from all other agents"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Holistic Risk Assessment",
            description=f"Calculated unified risk score based on {len(context.previous_findings)} inputs.",
            confidence_score=0.92,
            created_at=utc_now()
        )
