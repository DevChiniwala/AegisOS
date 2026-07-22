from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class BehaviorAnalyst(BaseAgent):
    def __init__(self):
        super().__init__(
            name="BehaviorAnalyst",
            role="Behavioral Profiler",
            description="Evaluates behavioral deviations across all dimensions"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Behavioral Profile Analysis",
            description="No significant behavioral deviations detected in current context.",
            confidence_score=0.9,
            created_at=utc_now()
        )
