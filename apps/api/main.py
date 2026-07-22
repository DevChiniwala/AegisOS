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
    # Initialize services here
    yield
    logger.info("Shutting down AegisOS API...")
    # Cleanup here

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
