"""
Temporal Activities wrapping LangGraph sub-graph execution.

Each activity is an independently retryable unit of work. Activities invoke
LangGraph nodes grouped by investigation phase:
- Triage: planner → triage → entity_resolution → graph_analysis
- Deep Investigation: timeline → behavior → risk_assessment → root_cause
- Compliance & Decision: compliance → recommendation → narrative → reflector → decision
"""

from typing import Any, Dict, List

from temporalio import activity

from core.utils.logging import get_logger

logger = get_logger(__name__)


@activity.defn
async def run_triage_agents(
    case_id: str,
    transaction: Dict[str, Any],
    risk_score: float,
    features: Dict[str, float],
) -> Dict[str, Any]:
    """Execute triage sub-graph: planner → triage → entity_resolution → graph_analysis."""
    activity.heartbeat("starting triage phase")

    from services.agents.langgraph_orchestrator import InvestigationState, build_triage_subgraph

    subgraph = build_triage_subgraph()
    if subgraph is None:
        return _fallback_triage(transaction, risk_score, features)

    initial_state: InvestigationState = {
        "transaction": transaction,
        "risk_score": risk_score,
        "features": features,
        "messages": [],
        "evidence": [],
        "findings": [],
        "agent_outputs": [],
        "verdict": "",
        "confidence": 0.0,
        "should_file_sar": False,
        "case_id": case_id,
        "investigation_plan": [],
        "root_causes": [],
        "recommendations": [],
        "narrative": "",
    }

    config = {"configurable": {"thread_id": f"{case_id}-triage"}}
    result = subgraph.invoke(initial_state, config=config)

    activity.heartbeat("triage phase complete")

    return {
        "findings": result.get("findings", []),
        "evidence": result.get("evidence", []),
        "agent_outputs": result.get("agent_outputs", []),
        "investigation_plan": result.get("investigation_plan", []),
        "agent_count": len(result.get("agent_outputs", [])),
    }


@activity.defn
async def run_deep_investigation(
    case_id: str,
    transaction: Dict[str, Any],
    risk_score: float,
    features: Dict[str, float],
    triage_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Execute deep investigation: timeline → behavior → risk_assessment → root_cause."""
    activity.heartbeat("starting deep investigation")

    from services.agents.langgraph_orchestrator import InvestigationState, build_deep_subgraph

    subgraph = build_deep_subgraph()
    if subgraph is None:
        return _fallback_deep(transaction, risk_score, features, triage_result)

    initial_state: InvestigationState = {
        "transaction": transaction,
        "risk_score": risk_score,
        "features": features,
        "messages": [],
        "evidence": triage_result.get("evidence", []),
        "findings": triage_result.get("findings", []),
        "agent_outputs": triage_result.get("agent_outputs", []),
        "verdict": "",
        "confidence": 0.0,
        "should_file_sar": False,
        "case_id": case_id,
        "investigation_plan": triage_result.get("investigation_plan", []),
        "root_causes": [],
        "recommendations": [],
        "narrative": "",
    }

    config = {"configurable": {"thread_id": f"{case_id}-deep"}}
    result = subgraph.invoke(initial_state, config=config)

    activity.heartbeat("deep investigation complete")

    return {
        "findings": result.get("findings", []),
        "evidence": result.get("evidence", []),
        "agent_outputs": result.get("agent_outputs", []),
        "root_causes": result.get("root_causes", []),
        "agent_count": len(result.get("agent_outputs", [])),
    }


@activity.defn
async def run_compliance_and_decision(
    case_id: str,
    transaction: Dict[str, Any],
    risk_score: float,
    features: Dict[str, float],
    investigation_result: Dict[str, Any],
    additional_evidence: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Execute compliance & decision: compliance → recommendation → narrative → reflector → decision."""
    activity.heartbeat("starting compliance and decision phase")

    from services.agents.langgraph_orchestrator import InvestigationState, build_decision_subgraph

    subgraph = build_decision_subgraph()
    if subgraph is None:
        return _fallback_decision(transaction, risk_score, investigation_result)

    all_evidence = investigation_result.get("evidence", []) + additional_evidence

    initial_state: InvestigationState = {
        "transaction": transaction,
        "risk_score": risk_score,
        "features": features,
        "messages": [],
        "evidence": all_evidence,
        "findings": investigation_result.get("findings", []),
        "agent_outputs": investigation_result.get("agent_outputs", []),
        "verdict": "",
        "confidence": 0.0,
        "should_file_sar": False,
        "case_id": case_id,
        "investigation_plan": [],
        "root_causes": investigation_result.get("root_causes", []),
        "recommendations": [],
        "narrative": "",
    }

    config = {"configurable": {"thread_id": f"{case_id}-decision"}}
    result = subgraph.invoke(initial_state, config=config)

    activity.heartbeat("compliance and decision complete")

    return {
        "verdict": result.get("verdict", "UNKNOWN"),
        "confidence": result.get("confidence", 0.0),
        "findings": result.get("findings", []),
        "narrative": result.get("narrative", ""),
        "should_file_sar": result.get("should_file_sar", False),
        "recommendations": result.get("recommendations", []),
        "agent_count": len(result.get("agent_outputs", [])),
    }


def _fallback_triage(
    transaction: Dict[str, Any], risk_score: float, features: Dict[str, float]
) -> Dict[str, Any]:
    """Fallback when LangGraph is not available."""
    if risk_score > 0.8:
        verdict = "HIGH RISK — immediate review required"
    elif risk_score > 0.5:
        verdict = "MODERATE RISK — further analysis needed"
    else:
        verdict = "LOW RISK — routine monitoring"

    return {
        "findings": [f"Triage: {verdict}"],
        "evidence": [],
        "agent_outputs": [{"agent": "triage_fallback", "assessment": verdict}],
        "investigation_plan": ["basic_verification"],
        "agent_count": 1,
    }


def _fallback_deep(
    transaction: Dict[str, Any],
    risk_score: float,
    features: Dict[str, float],
    triage_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Fallback deep investigation without LangGraph."""
    findings = list(triage_result.get("findings", []))
    findings.append(f"Deep investigation: risk_score={risk_score:.3f}")

    causes = []
    if features.get("is_new_device", 0) == 1.0:
        causes.append("Account takeover via compromised credentials")
    if features.get("transaction_velocity_1h", 0) > 5:
        causes.append("Automated/bot-driven attack pattern")

    return {
        "findings": findings,
        "evidence": triage_result.get("evidence", []),
        "agent_outputs": [{"agent": "deep_fallback", "risk_score": risk_score}],
        "root_causes": causes,
        "agent_count": 1,
    }


def _fallback_decision(
    transaction: Dict[str, Any],
    risk_score: float,
    investigation_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Fallback decision without LangGraph."""
    if risk_score > 0.9:
        verdict, confidence = "BLOCK", 0.95
    elif risk_score > 0.7:
        verdict, confidence = "ESCALATE", 0.85
    elif risk_score > 0.4:
        verdict, confidence = "REVIEW", 0.7
    else:
        verdict, confidence = "APPROVE", 0.9

    should_sar = risk_score > 0.85
    recommendations = []
    if should_sar:
        recommendations = ["Block transaction", "Freeze account", "File SAR"]
    elif risk_score > 0.6:
        recommendations = ["Flag for manual review", "Enhanced monitoring 90 days"]

    amount = transaction.get("amount", 0)
    sender = transaction.get("sender_id", "unknown")
    narrative = (
        f"Transaction from {sender} for ${amount} assessed at risk {risk_score:.3f}. "
        f"Verdict: {verdict} with confidence {confidence:.2f}."
    )

    return {
        "verdict": verdict,
        "confidence": confidence,
        "findings": [f"Decision: {verdict} (confidence={confidence:.2f})"],
        "narrative": narrative,
        "should_file_sar": should_sar,
        "recommendations": recommendations,
        "agent_count": 1,
    }
