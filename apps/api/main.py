"""
AegisOS API Main Application Entrypoint.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from core.config.settings import get_settings
from core.utils.logging import get_logger
from apps.api.middleware import RequestIDMiddleware, RateLimitMiddleware, AuditMiddleware, TimingMiddleware
from apps.api.routes import transactions, investigations, entities, graph, risk, auth, admin, streaming, dashboard

logger = get_logger(__name__)

class AegisError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting AegisOS API...")

    from core.events import get_event_bus, shutdown_event_bus
    from apps.api.dependencies import (
        get_feature_engine, get_risk_engine, get_graph_engine,
        get_behavioral_engine, get_investigation_orchestrator,
        get_memory_engine, get_explainability_engine,
    )

    app.state.event_bus = await get_event_bus()
    app.state.feature_engine = get_feature_engine()
    app.state.risk_engine = get_risk_engine()
    app.state.graph_engine = get_graph_engine()
    app.state.behavioral_engine = get_behavioral_engine()
    app.state.orchestrator = get_investigation_orchestrator()
    app.state.memory_engine = get_memory_engine()
    app.state.explainability_engine = get_explainability_engine()

    logger.info("All engines initialized successfully")
    yield
    logger.info("Shutting down AegisOS API...")
    await shutdown_event_bus()

app = FastAPI(
    title="AegisOS API",
    version="0.1.0",
    description="The Autonomous AI Operating System for Financial Intelligence",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Transactions", "description": "Transaction scoring and management"},
        {"name": "Investigations", "description": "Case management and investigations"},
        {"name": "Entities", "description": "User, merchant, and device profiles"},
        {"name": "Graph", "description": "Knowledge graph operations"},
        {"name": "Risk", "description": "Risk management and thresholds"},
        {"name": "Auth", "description": "Authentication and authorization"},
        {"name": "Admin", "description": "System administration and metrics"},
        {"name": "Streaming", "description": "WebSocket streams"},
        {"name": "Dashboard", "description": "Dashboard analytics"},
    ]
)

# Middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if hasattr(settings, "allowed_origins") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TimingMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)

# Exception Handlers
@app.exception_handler(AegisError)
async def aegis_error_handler(request: Request, exc: AegisError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_code": "AEGIS_ERROR"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_code": "INTERNAL_ERROR"}
    )

# Routers
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(investigations.router, prefix="/api/v1/investigations", tags=["Investigations"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["Entities"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["Graph"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(streaming.router, prefix="/api/v1/ws", tags=["Streaming"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/health", tags=["System"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}


@app.get("/ready", tags=["System"])
async def readiness_check():
    """Readiness probe — checks all critical dependencies."""
    checks = {}

    checks["risk_engine"] = hasattr(app.state, "risk_engine") and app.state.risk_engine is not None
    checks["feature_engine"] = hasattr(app.state, "feature_engine") and app.state.feature_engine is not None
    checks["event_bus"] = hasattr(app.state, "event_bus") and app.state.event_bus is not None

    try:
        import redis as redis_lib
        r = redis_lib.Redis(host="localhost", port=6379, socket_timeout=1)
        r.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False

    all_ready = all(v for k, v in checks.items() if k != "redis")
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": time.time(),
    }


@app.get("/metrics", tags=["System"])
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import PlainTextResponse
    from core.telemetry import metrics
    return PlainTextResponse(metrics.prometheus_text(), media_type="text/plain")
