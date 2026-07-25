"""
Investigation routes — wired to orchestrator.
"""

from fastapi import APIRouter, Request

from core.schemas.investigation import CaseStatus
from core.schemas.transaction import TransactionCreate

router = APIRouter()


@router.post("/")
async def trigger_investigation(transaction: TransactionCreate, request: Request):
    """Trigger a full multi-agent investigation on a transaction."""
    feature_engine = request.app.state.feature_engine
    risk_engine = request.app.state.risk_engine
    orchestrator = request.app.state.orchestrator

    features = feature_engine.extract_features(
        transaction=transaction,
        user=None,
        merchant=None,
        device=None,
        history=[]
    )
    scoring_result = risk_engine.score_transaction(transaction, features)
    case = await orchestrator.run_investigation(transaction, scoring_result)

    return {
        "status": "completed",
        "case_id": case.case_id,
        "priority": case.priority.value,
        "findings_count": len(case.findings),
    }


@router.get("/{case_id}")
async def get_investigation(case_id: str, request: Request):
    """Get investigation case details from memory engine."""
    memory_engine = request.app.state.memory_engine
    case = memory_engine.get_case(case_id)
    if case:
        return case
    return {"error": "Case not found", "case_id": case_id}


@router.get("/")
async def list_investigations():
    """List investigations."""
    return []


@router.patch("/{case_id}")
async def update_investigation(case_id: str, status: CaseStatus):
    """Update investigation status."""
    return {"status": "updated", "case_id": case_id, "new_status": status}


@router.get("/{case_id}/timeline")
async def get_timeline(case_id: str):
    """Get investigation timeline."""
    return []


@router.get("/{case_id}/report")
async def get_report(case_id: str):
    """Get investigation report."""
    return {"report": f"Report for case {case_id}"}
