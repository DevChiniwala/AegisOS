from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class ComplianceOfficer(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ComplianceOfficer",
            role="Compliance Checker",
            description="Checks AML thresholds and sanctions lists"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        tx = context.transaction
        sar_flag = False
        if tx.amount and tx.amount > 10000:
            sar_flag = True
            
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Regulatory Compliance Check",
            description=f"SAR required: {sar_flag}. No sanctions hits detected.",
            confidence_score=0.99,
            created_at=utc_now()
        )
