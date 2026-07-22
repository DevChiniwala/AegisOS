"""
Admin endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def admin_health():
    return {"services": {"db": "ok", "redis": "ok", "kafka": "ok"}}

@router.get("/metrics")
async def get_metrics():
    return {"latency": 50, "throughput": 1000, "queue_depth": 10}

@router.get("/models")
async def list_models():
    return []

@router.post("/models/{model_name}/reload")
async def reload_model(model_name: str):
    return {"status": f"reloaded {model_name}"}

@router.get("/audit-log")
async def get_audit_log():
    return []
