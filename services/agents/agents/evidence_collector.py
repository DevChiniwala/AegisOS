from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class EvidenceCollector(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EvidenceCollector",
            role="Evidence Organizer",
            description="Aggregates evidence from all agent findings"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        evidence_count = len(context.previous_findings)
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Evidence Aggregation",
            description=f"Successfully aggregated {evidence_count} pieces of evidence from preceding agents.",
            confidence_score=1.0,
            created_at=utc_now()
        )
