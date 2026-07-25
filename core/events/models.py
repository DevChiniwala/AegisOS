"""Immutable event models for event sourcing."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List
from uuid import uuid4


class EventType(str, Enum):
    # Investigation lifecycle
    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_STARTED = "investigation.started"
    INVESTIGATION_AGENT_DISPATCHED = "investigation.agent_dispatched"
    INVESTIGATION_AGENT_COMPLETED = "investigation.agent_completed"
    INVESTIGATION_FINDING_ADDED = "investigation.finding_added"
    INVESTIGATION_EVIDENCE_COLLECTED = "investigation.evidence_collected"
    INVESTIGATION_VERDICT_REACHED = "investigation.verdict_reached"
    INVESTIGATION_CLOSED = "investigation.closed"
    INVESTIGATION_ESCALATED = "investigation.escalated"

    # Transaction events
    TRANSACTION_SCORED = "transaction.scored"
    TRANSACTION_BLOCKED = "transaction.blocked"
    TRANSACTION_APPROVED = "transaction.approved"
    TRANSACTION_FLAGGED = "transaction.flagged"

    # Compliance events
    SAR_GENERATED = "compliance.sar_generated"
    SAR_FILED = "compliance.sar_filed"
    SANCTIONS_MATCH = "compliance.sanctions_match"

    # System events
    SYSTEM_ALERT = "system.alert"
    MODEL_DRIFT_DETECTED = "system.model_drift"


@dataclass(frozen=True)
class InvestigationEvent:
    """Immutable event in an investigation's event stream."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = EventType.INVESTIGATION_CREATED
    case_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    reasoning_chain: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    sequence_number: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "case_id": self.case_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_name": self.agent_name,
            "data": self.data,
            "reasoning_chain": list(self.reasoning_chain),
            "confidence": self.confidence,
            "metadata": self.metadata,
            "sequence_number": self.sequence_number,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InvestigationEvent":
        return cls(
            event_id=d["event_id"],
            event_type=EventType(d["event_type"]),
            case_id=d.get("case_id", ""),
            timestamp=datetime.fromisoformat(d["timestamp"]) if isinstance(d.get("timestamp"), str) else d.get("timestamp", datetime.now(timezone.utc)),
            agent_name=d.get("agent_name", ""),
            data=d.get("data", {}),
            reasoning_chain=d.get("reasoning_chain", []),
            confidence=d.get("confidence", 0.0),
            metadata=d.get("metadata", {}),
            sequence_number=d.get("sequence_number", 0),
        )
