from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class ReportGenerator(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ReportGenerator",
            role="Technical Writer",
            description="Generates structured investigation report"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        findings_summary = "\n".join([f"- {f.title}: {f.description}" for f in context.previous_findings])
        report = f"Executive Summary:\nInvestigation complete for transaction {context.transaction.transaction_id}.\n\nFindings:\n{findings_summary}"
        
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Final Report",
            description=report,
            confidence_score=1.0,
            created_at=utc_now()
        )
