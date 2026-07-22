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
        features = context.features
        anomalies = []
        confidence = 0.5

        amount = float(tx.amount) if tx.amount else 0.0
        if amount > 10000:
            anomalies.append(f"High transaction amount: ${amount:,.2f}")
            confidence += 0.1

        zscore = features.get('amount_zscore', 0.0)
        if abs(zscore) > 3.0:
            anomalies.append(f"Amount z-score {zscore:.2f} exceeds 3 standard deviations")
            confidence += 0.15

        ratio = features.get('amount_to_max_ratio', 0.0)
        if ratio > 2.0:
            anomalies.append(f"Amount is {ratio:.1f}x the user's historical max")
            confidence += 0.1

        if features.get('is_round_amount', 0.0) == 1.0 and amount > 5000:
            anomalies.append("Suspicious round amount pattern (structuring indicator)")
            confidence += 0.05

        if features.get('currency_is_foreign', 0.0) == 1.0:
            anomalies.append("Cross-border transaction detected")
            confidence += 0.05

        if context.risk_score > 0.8:
            anomalies.append(f"Risk score elevated at {context.risk_score:.2f}")
            confidence += 0.1

        confidence = min(confidence, 0.99)
        desc = f"Found {len(anomalies)} anomalies: {'; '.join(anomalies)}" if anomalies else "No significant transaction anomalies detected"

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Transaction Pattern Analysis",
            description=desc,
            confidence_score=confidence,
            created_at=utc_now()
        )
