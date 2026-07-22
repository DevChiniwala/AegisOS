from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import Field
from uuid import UUID
from .base import BaseSchema


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    TRIAGING = "TRIAGING"
    INVESTIGATING = "INVESTIGATING"
    EVIDENCE_REVIEW = "EVIDENCE_REVIEW"
    DECIDED = "DECIDED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Finding(BaseSchema):
    finding_id: str
    agent_name: str
    finding_type: str
    description: str
    confidence: float
    evidence_refs: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Evidence(BaseSchema):
    evidence_id: str
    type: str
    source: str
    content: Any
    metadata: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TimelineEvent(BaseSchema):
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    description: str
    agent_name: str
    data: Dict[str, Any]


class InvestigationCase(BaseSchema):
    case_id: str
    transaction_ids: List[str]
    entity_ids: List[str]
    status: CaseStatus
    priority: CasePriority
    risk_score: float
    assigned_to: Optional[str] = None
    findings: List[Finding] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    verdict: Optional[str] = None
    sar_generated: bool = False
