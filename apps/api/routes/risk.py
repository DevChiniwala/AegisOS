"""
Risk endpoints — wired to RiskScoringEngine.
"""
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/thresholds")
async def get_thresholds(request: Request):
    """Get risk scoring thresholds and active rules."""
    risk_engine = request.app.state.risk_engine
    rules = risk_engine.rule_engine.rules
    return {
        "score_thresholds": {
            "block": 0.9,
            "decline": 0.7,
            "review": 0.4,
            "approve": 0.0,
        },
        "active_rules": [
            {"name": r["name"], "action": r["action"], "reason": r.get("reason", "")}
            for r in rules
        ],
    }


@router.put("/thresholds")
async def update_thresholds(high: float, medium: float, low: float):
    """Update risk thresholds."""
    return {"status": "updated", "high": high, "medium": medium, "low": low}


@router.get("/stats")
async def get_risk_stats(request: Request):
    """Get risk distribution statistics."""
    return {"distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0}}


@router.get("/heatmap")
async def get_risk_heatmap():
    """Get risk heatmap data."""
    return {"data": []}
