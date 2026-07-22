from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import Field
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.schemas.base import BaseSchema, UUIDMixin

logger = structlog.get_logger(__name__)


class AuditEntry(BaseSchema, UUIDMixin):
    user_id: Optional[str] = None
    action: str
    resource: str
    status: str
    ip_address: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditLogger:
    @staticmethod
    async def log_event(
        action: str,
        resource: str,
        status: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        entry = AuditEntry(
            action=action,
            resource=resource,
            status=status,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {}
        )
        # Log to structured logger; a real implementation would also write to DB/Kafka
        logger.info(
            "audit_event",
            audit_id=str(entry.id),
            action=entry.action,
            resource=entry.resource,
            status=entry.status,
            user_id=entry.user_id,
            ip_address=entry.ip_address
        )


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        start_time = datetime.utcnow()
        response = await call_next(request)
        
        # Log the request/response cycle
        await AuditLogger.log_event(
            action=f"{request.method} {request.url.path}",
            resource="API",
            status=str(response.status_code),
            ip_address=request.client.host if request.client else None,
            details={
                "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }
        )
        return response
