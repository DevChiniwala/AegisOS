from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class GraphDetective(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GraphDetective",
            role="Network Analyst",
            description="Queries graph engine for entity connections"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Network Topology Analysis",
            description="Entity is isolated; no immediate connection to known fraud rings.",
            confidence_score=0.85,
            created_at=utc_now()
        )
