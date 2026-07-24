"""Reflector Agent — Validates reasoning quality and checks for gaps."""
import uuid
from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now


class ReflectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Reflector",
            role="Quality Assurance Analyst",
            description="Validates investigation reasoning quality, identifies gaps in evidence, checks for logical inconsistencies, and ensures conclusion confidence is warranted",
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        previous = context.previous_findings
        risk = context.risk_score
        issues = []
        confidence = 0.7

        if len(previous) < 3:
            issues.append("COVERAGE GAP: Fewer than 3 agents contributed findings — insufficient analysis depth")
            confidence -= 0.1

        confidences = [f.confidence_score for f in previous]
        if confidences:
            avg_conf = sum(confidences) / len(confidences)
            max_conf = max(confidences)
            min_conf = min(confidences)

            if max_conf - min_conf > 0.5:
                issues.append(
                    f"DISAGREEMENT: Agent confidence spread is {max_conf - min_conf:.2f} — "
                    "significant analytical disagreement"
                )
                confidence -= 0.1

            if avg_conf > 0.8 and risk < 0.3:
                issues.append(
                    "INCONSISTENCY: High agent confidence but low risk score — "
                    "possible false positive or model calibration issue"
                )
                confidence -= 0.15

            if avg_conf < 0.4 and risk > 0.7:
                issues.append(
                    "UNCERTAINTY: Low agent confidence despite high risk score — "
                    "insufficient evidence for confident decision"
                )
                confidence -= 0.1

        agent_names = set(f.agent_name for f in previous)
        expected_agents = {"TransactionInvestigator", "GraphDetective", "BehaviorAnalyst"}
        missing = expected_agents - agent_names
        if missing:
            issues.append(f"MISSING PERSPECTIVES: {', '.join(missing)} did not contribute")
            confidence -= 0.05

        has_graph = any("graph" in f.description.lower() or "network" in f.description.lower() for f in previous)
        has_temporal = any("time" in f.description.lower() or "velocity" in f.description.lower() for f in previous)
        if not has_graph:
            issues.append("NO GRAPH ANALYSIS: Network topology not examined")
        if not has_temporal:
            issues.append("NO TEMPORAL ANALYSIS: Time-based patterns not examined")

        confidence = max(confidence, 0.3)
        if not issues:
            desc = "Investigation reasoning is sound: adequate coverage, consistent findings, no gaps detected"
            confidence = 0.9
        else:
            desc = "; ".join(issues)

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Reasoning Quality Assessment",
            description=desc,
            confidence_score=confidence,
            created_at=utc_now(),
        )
