from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import Field

from .base import BaseSchema


def utc_now():
    return datetime.now(timezone.utc)


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
    timestamp: datetime = Field(default_factory=utc_now)
    source_service: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    version: str = "1.0"


class InvestigationEvent(BaseSchema):
    """Immutable event for the CQRS event-sourced investigation log."""
    event_id: UUID = Field(default_factory=uuid4)
    case_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: Literal[
        "ALERT_RECEIVED", 
        "AGENT_DISPATCHED", 
        "EVIDENCE_FOUND",
        "HYPOTHESIS_FORMED", 
        "HYPOTHESIS_REJECTED", 
        "HUMAN_REVIEW_REQUESTED",
        "VERDICT_RENDERED", 
        "SAR_GENERATED", 
        "CASE_CLOSED"
    ]
    agent_name: Optional[str] = None
    payload: Dict[str, Any]
    reasoning_chain: List[str] = Field(default_factory=list)
    confidence: float = 0.0
