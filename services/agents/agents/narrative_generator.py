"""Narrative Generator Agent — Produces SAR reports and executive summaries."""
import uuid
from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
from services.agents.llm_factory import get_llm


class NarrativeGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NarrativeGenerator",
            role="Report Writer",
            description="Generates FinCEN-compliant SAR narratives and executive summaries from investigation findings with evidence citations",
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        findings = context.previous_findings
        tx = context.transaction
        risk = context.risk_score

        evidence_summary = []
        for f in findings:
            evidence_summary.append(f"[{f.agent_name}] {f.description}")

        llm = get_llm()
        if llm and risk > 0.7:
            try:
                prompt = (
                    "You are a BSA/AML compliance officer. Generate a concise SAR narrative "
                    "based on the following investigation findings. Include: who, what, when, "
                    "where, why, and how. Cite specific evidence.\n\n"
                    f"Transaction: amount={tx.amount}, sender={tx.sender_id}, receiver={tx.receiver_id}\n"
                    f"Risk Score: {risk:.3f}\n\n"
                    f"Findings:\n" + "\n".join(evidence_summary[-10:])
                )
                response = llm.invoke(prompt)
                narrative = response.content
            except Exception:
                narrative = self._generate_template_narrative(tx, risk, findings)
        else:
            narrative = self._generate_template_narrative(tx, risk, findings)

        self.memory.store("sar_narrative", narrative)

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Investigation Narrative",
            description=narrative[:500],
            confidence_score=0.85,
            created_at=utc_now(),
        )

    def _generate_template_narrative(self, tx, risk: float, findings) -> str:
        finding_count = len(findings)
        high_conf = [f for f in findings if f.confidence_score > 0.7]

        if risk > 0.85:
            severity = "critical"
            action = "immediate blocking and SAR filing"
        elif risk > 0.6:
            severity = "elevated"
            action = "enhanced monitoring and manual review"
        else:
            severity = "low"
            action = "routine monitoring"

        narrative = (
            f"SUMMARY: Transaction by {tx.sender_id} to {tx.receiver_id} for "
            f"{tx.currency} {tx.amount} has been assessed as {severity} risk "
            f"(score: {risk:.3f}). Investigation involved {finding_count} analytical "
            f"dimensions with {len(high_conf)} high-confidence findings. "
            f"Recommended action: {action}."
        )
        return narrative
