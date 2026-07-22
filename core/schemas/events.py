from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import Field
from uuid import UUID, uuid4
from .base import BaseSchema


class EventType(str, Enum):
    TRANSACTION_RECEIVED = "TRANSACTION_RECEIVED"
    TRANSACTION_SCORED = "TRANSACTION_SCORED"
    ALERT_GENERATED = "ALERT_GENERATED"
    INVESTIGATION_STARTED = "INVESTIGATION_STARTED"
    INVESTIGATION_COMPLETED = "INVESTIGATION_COMPLETED"
    MODEL_UPDATED = "MODEL_UPDATED"
    RISK_THRESHOLD_CHANGED = "RISK_THRESHOLD_CHANGED"


class EventEnvelope(BaseSchema):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    version: str = "1.0"
