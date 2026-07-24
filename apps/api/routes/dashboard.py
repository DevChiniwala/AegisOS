"""
Dashboard endpoints — wired to engines for real metrics.
"""
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/overview")
async def get_overview(request: Request):
    """Get dashboard overview with live stats."""
    risk_engine = request.app.state.risk_engine
    rules_count = len(risk_engine.rule_engine.rules)
    models_count = len(risk_engine.ensemble.models)

    return {
        "active_rules": rules_count,
        "active_models": models_count,
        "scoring_engine": "adaptive_ensemble",
        "calibration": {
            "a": risk_engine.ensemble._calibration_a,
            "b": risk_engine.ensemble._calibration_b,
        },
    }


@router.get("/timeline")
async def get_timeline():
    """Get scoring timeline data."""
    return {"data": []}


@router.get("/top-risks")
async def get_top_risks():
    """Get highest risk entities."""
    return []


@router.get("/model-performance")
async def get_model_performance(request: Request):
    """Get model performance metrics."""
    risk_engine = request.app.state.risk_engine
    models_info = [
        {"name": m.model_name, "version": m.model_version}
        for m in risk_engine.ensemble.models
    ]
    return {"models": models_info}
