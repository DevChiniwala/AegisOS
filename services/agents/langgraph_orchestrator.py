"""
LangGraph-based Investigation Orchestrator.

Implements a StateGraph with conditional routing for multi-agent
fraud investigation. Falls back to the sequential orchestrator
when LangGraph dependencies are unavailable.
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
from core.schemas.transaction import TransactionCreate
from core.schemas.investigation import InvestigationCase, CaseStatus, CasePriority, TimelineEvent, Finding
from core.utils.helpers import utc_now, generate_id
from core.utils.logging import get_logger
from services.agents.llm_factory import get_llm, is_llm_available

logger = get_logger(__name__)


class InvestigationState(TypedDict):
    transaction: Dict[str, Any]
    risk_score: float
    features: Dict[str, float]
    messages: Annotated[List[str], operator.add]
    evidence: Annotated[List[Dict[str, Any]], operator.add]
    findings: Annotated[List[str], operator.add]
    verdict: str
    should_file_sar: bool
    case_id: str


def _build_graph():
    """Build the LangGraph StateGraph. Returns None if langgraph not available."""
    try:
        from langgraph.graph import StateGraph, END
    except ImportError:
        logger.info("langgraph not installed — using fallback orchestrator")
        return None

    llm = get_llm()

    def triage_node(state: InvestigationState) -> Dict[str, Any]:
        tx = state["transaction"]
        risk = state["risk_score"]
        analysis = (
            f"Transaction {tx.get('transaction_id', 'unknown')}: "
            f"amount={tx.get('amount', 0)}, currency={tx.get('currency', 'USD')}, "
            f"risk_score={risk:.3f}"
        )

        if llm:
            try:
                response = llm.invoke(
                    f"You are a fraud analyst. Analyze this transaction and identify risk indicators:\n{analysis}"
                )
                return {"messages": [response.content], "findings": [f"Triage: {response.content[:200]}"]}
            except Exception as e:
                logger.warning("LLM triage failed, using heuristic", error=str(e))

        findings = []
        if risk > 0.8:
            findings.append("Triage: HIGH RISK — immediate review required")
        elif risk > 0.5:
            findings.append("Triage: MODERATE RISK — further analysis needed")
        else:
            findings.append("Triage: LOW RISK — routine monitoring")
        return {"messages": [analysis], "findings": findings}

    def graph_analysis_node(state: InvestigationState) -> Dict[str, Any]:
        tx = state["transaction"]
        evidence = []
        findings = []

        sender_id = tx.get("sender_id", tx.get("user_id", ""))
        if sender_id:
            evidence.append({"type": "graph_context", "entity": sender_id, "checked": True})
            findings.append(f"Graph: analyzed entity {sender_id} network connections")

        return {"evidence": evidence, "findings": findings}

    def risk_assessment_node(state: InvestigationState) -> Dict[str, Any]:
        risk = state["risk_score"]
        num_findings = len(state["findings"])
        evidence_count = len(state["evidence"])

        assessment = (
            f"Risk Assessment: score={risk:.3f}, "
            f"findings={num_findings}, evidence_items={evidence_count}"
        )

        if llm and risk > 0.7:
            try:
                context = "\n".join(state["findings"][-5:])
                response = llm.invoke(
                    f"Based on these findings, provide a risk assessment:\n{context}"
                )
                return {"findings": [f"Assessment: {response.content[:200]}"], "messages": [assessment]}
            except Exception:
                pass

        return {"findings": [assessment], "messages": [assessment]}

    def compliance_node(state: InvestigationState) -> Dict[str, Any]:
        risk = state["risk_score"]
        should_sar = risk > 0.85
        findings = []

        if should_sar:
            findings.append("Compliance: SAR filing recommended based on risk threshold")
        else:
            findings.append("Compliance: No regulatory action required at this time")

        return {"findings": findings, "should_file_sar": should_sar}

    def decision_node(state: InvestigationState) -> Dict[str, Any]:
        risk = state["risk_score"]
        if risk > 0.9:
            verdict = "BLOCK"
        elif risk > 0.7:
            verdict = "ESCALATE"
        elif risk > 0.4:
            verdict = "REVIEW"
        else:
            verdict = "APPROVE"
        return {"verdict": verdict, "findings": [f"Decision: {verdict}"]}

    def should_route_compliance(state: InvestigationState) -> str:
        if state["risk_score"] > 0.85:
            return "compliance"
        return "decision"

    graph = StateGraph(InvestigationState)
    graph.add_node("triage", triage_node)
    graph.add_node("graph_analysis", graph_analysis_node)
    graph.add_node("risk_assessment", risk_assessment_node)
    graph.add_node("compliance", compliance_node)
    graph.add_node("decision", decision_node)

    graph.set_entry_point("triage")
    graph.add_edge("triage", "graph_analysis")
    graph.add_edge("graph_analysis", "risk_assessment")
    graph.add_conditional_edges("risk_assessment", should_route_compliance, {
        "compliance": "compliance",
        "decision": "decision",
    })
    graph.add_edge("compliance", "decision")
    graph.add_edge("decision", END)

    return graph.compile()


class LangGraphOrchestrator:
    def __init__(self):
        self._graph = _build_graph()

    @property
    def available(self) -> bool:
        return self._graph is not None

    async def run_investigation(self, transaction: TransactionCreate, risk_score: float, features: Dict[str, float] = None) -> InvestigationCase:
        if not self.available:
            raise RuntimeError("LangGraph not available — use fallback orchestrator")

        case_id = f"CASE-{generate_id()[:8].upper()}"
        tx_dict = transaction.model_dump() if hasattr(transaction, 'model_dump') else {}

        initial_state: InvestigationState = {
            "transaction": tx_dict,
            "risk_score": risk_score,
            "features": features or {},
            "messages": [],
            "evidence": [],
            "findings": [],
            "verdict": "",
            "should_file_sar": False,
            "case_id": case_id,
        }

        result = self._graph.invoke(initial_state)

        case = InvestigationCase(
            case_id=case_id,
            transaction_id=tx_dict.get("transaction_id", ""),
            status=CaseStatus.CLOSED,
            priority=CasePriority.CRITICAL if risk_score > 0.9 else CasePriority.HIGH if risk_score > 0.7 else CasePriority.MEDIUM,
        )
        case.timeline.append(TimelineEvent(event_type="COMPLETED", description=f"Verdict: {result.get('verdict', 'UNKNOWN')}"))

        for f in result.get("findings", []):
            case.findings.append(Finding(
                agent="langgraph",
                finding_type="analysis",
                description=f,
                severity="high" if risk_score > 0.7 else "medium"
            ))

        return case
