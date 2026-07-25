"""
Temporal Workflow definitions for durable investigation orchestration.

The InvestigationWorkflow coordinates LangGraph agent execution with:
- Phased execution (triage → deep investigation → compliance/decision)
- HITL gates for high-risk cases (72h timeout with escalation)
- Signal-based analyst intervention (approve, reject, add evidence)
- Per-phase retry policies and timeouts
"""

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Dict, List, Optional

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from core.utils.logging import get_logger

logger = get_logger(__name__)

TASK_QUEUE = "aegis-investigations"


@dataclass
class InvestigationInput:
    case_id: str
    transaction: Dict[str, Any]
    risk_score: float
    features: Dict[str, float]
    investigation_plan: List[str] = field(default_factory=list)


@dataclass
class InvestigationResult:
    case_id: str
    verdict: str
    confidence: float
    findings: List[str]
    narrative: str
    should_file_sar: bool
    recommendations: List[str]
    root_causes: List[str] = field(default_factory=list)
    evidence_count: int = 0
    agent_count: int = 0


@workflow.defn
class InvestigationWorkflow:
    """Durable investigation workflow wrapping LangGraph agent execution.

    Phases:
    1. Triage (fast path: planner → triage → entity_resolution → graph_analysis)
    2. Deep Investigation (timeline → behavior → risk_assessment → root_cause)
    3. HITL Gate (for risk > 0.85: wait up to 72h for analyst decision)
    4. Compliance & Decision (compliance → recommendation → narrative → reflector → decision)
    """

    def __init__(self):
        self._human_decision: Optional[str] = None
        self._analyst_notes: List[str] = []
        self._additional_evidence: List[Dict[str, Any]] = []
        self._current_phase: str = "initializing"

    @workflow.run
    async def run(self, input: InvestigationInput) -> InvestigationResult:
        self._current_phase = "triage"

        triage_result = await workflow.execute_activity(
            "run_triage_agents",
            args=[input.case_id, input.transaction, input.risk_score, input.features],
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        self._current_phase = "deep_investigation"

        if input.risk_score > 0.6:
            deep_result = await workflow.execute_activity(
                "run_deep_investigation",
                args=[input.case_id, input.transaction, input.risk_score, input.features, triage_result],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=2,
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=30),
                ),
            )
        else:
            deep_result = triage_result

        if input.risk_score > 0.85:
            self._current_phase = "awaiting_analyst"

            try:
                await workflow.wait_condition(
                    lambda: self._human_decision is not None,
                    timeout=timedelta(hours=72),
                )
            except TimeoutError:
                self._analyst_notes.append("Auto-escalated: no analyst response within 72 hours")
                self._human_decision = "escalate"

            if self._human_decision == "reject":
                return InvestigationResult(
                    case_id=input.case_id,
                    verdict="ANALYST_OVERRIDE_CLEARED",
                    confidence=1.0,
                    findings=deep_result.get("findings", []),
                    narrative="Investigation closed by analyst — determined no action required.",
                    should_file_sar=False,
                    recommendations=["Analyst cleared transaction", *self._analyst_notes],
                    root_causes=[],
                    evidence_count=len(deep_result.get("evidence", [])),
                    agent_count=deep_result.get("agent_count", 0),
                )

        self._current_phase = "compliance_decision"

        merged_evidence = deep_result.get("evidence", []) + self._additional_evidence

        final_result = await workflow.execute_activity(
            "run_compliance_and_decision",
            args=[
                input.case_id,
                input.transaction,
                input.risk_score,
                input.features,
                deep_result,
                merged_evidence,
            ],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=15),
            ),
        )

        self._current_phase = "completed"

        all_findings = (
            triage_result.get("findings", [])
            + deep_result.get("findings", [])
            + final_result.get("findings", [])
        )

        return InvestigationResult(
            case_id=input.case_id,
            verdict=final_result.get("verdict", "UNKNOWN"),
            confidence=final_result.get("confidence", 0.0),
            findings=all_findings,
            narrative=final_result.get("narrative", ""),
            should_file_sar=final_result.get("should_file_sar", False),
            recommendations=final_result.get("recommendations", []),
            root_causes=deep_result.get("root_causes", []),
            evidence_count=len(merged_evidence),
            agent_count=final_result.get("agent_count", 0),
        )

    @workflow.signal
    async def analyst_approve(self, notes: str = ""):
        self._human_decision = "approve"
        if notes:
            self._analyst_notes.append(f"Approved: {notes}")

    @workflow.signal
    async def analyst_reject(self, notes: str = ""):
        self._human_decision = "reject"
        if notes:
            self._analyst_notes.append(f"Rejected: {notes}")

    @workflow.signal
    async def analyst_escalate(self, notes: str = ""):
        self._human_decision = "escalate"
        if notes:
            self._analyst_notes.append(f"Escalated: {notes}")

    @workflow.signal
    async def add_evidence(self, evidence: Dict[str, Any]):
        self._additional_evidence.append(evidence)
        self._analyst_notes.append(f"Evidence added: {evidence.get('type', 'unknown')}")

    @workflow.query
    def get_status(self) -> Dict[str, Any]:
        return {
            "phase": self._current_phase,
            "human_decision": self._human_decision,
            "analyst_notes": self._analyst_notes,
            "additional_evidence_count": len(self._additional_evidence),
        }
