"""
Investigation routes.
"""
from fastapi import APIRouter, Depends
from typing import List
from core.schemas.investigation import InvestigationCase, CaseStatus, CasePriority

router = APIRouter()

@router.post("/")
async def trigger_investigation(transaction_id: str):
    return {"status": "triggered", "transaction_id": transaction_id, "case_id": "case_123"}

@router.get("/{case_id}", response_model=InvestigationCase)
async def get_investigation(case_id: str):
    # Mock data
    return InvestigationCase(
        id=case_id,
        entity_id="entity_1",
        priority=CasePriority.HIGH,
        status=CaseStatus.OPEN,
        created_at="2023-10-27T10:00:00Z",
        updated_at="2023-10-27T10:00:00Z"
    )

@router.get("/", response_model=List[InvestigationCase])
async def list_investigations():
    return []

@router.patch("/{case_id}")
async def update_investigation(case_id: str, status: CaseStatus):
    return {"status": "updated", "case_id": case_id, "new_status": status}

@router.get("/{case_id}/timeline")
async def get_timeline(case_id: str):
    return []

@router.get("/{case_id}/report")
async def get_report(case_id: str):
    return {"report": f"Report for case {case_id}"}
