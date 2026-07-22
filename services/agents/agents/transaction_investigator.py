from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class TransactionInvestigator(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TransactionInvestigator",
            role="Financial Analyst",
            description="Analyzes transaction amount, frequency, timing patterns"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        tx = context.transaction
        anomalies = []
        confidence = 0.8
        
        if tx.amount and tx.amount > 10000:
            anomalies.append("Unusually high transaction amount")
            
        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Transaction Pattern Analysis",
            description=f"Found {len(anomalies)} anomalies: {', '.join(anomalies) if anomalies else 'None'}",
            confidence_score=confidence,
            created_at=utc_now()
        )
