"""
Dashboard endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/overview")
async def get_overview():
    return {
        "total_transactions": 10000,
        "fraud_rate": 0.015,
        "avg_score": 0.05,
        "alerts_today": 25
    }

@router.get("/timeline")
async def get_timeline():
    return {"data": []}

@router.get("/top-risks")
async def get_top_risks():
    return []

@router.get("/model-performance")
async def get_model_performance():
    return {
        "accuracy": 0.99,
        "precision": 0.85,
        "recall": 0.80,
        "f1": 0.82
    }
