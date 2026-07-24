"""Response models for the AegisOS Python SDK."""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class RiskScore(BaseModel):
    transaction_id: str
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: str
    verdict: str = ""
    reasons: list[str] = Field(default_factory=list)
    model_weights: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0.0


class Investigation(BaseModel):
    case_id: str
    transaction_id: str
    status: str
    verdict: Optional[str] = None
    confidence: float = 0.0
    summary: Optional[str] = None
    agents_involved: list[str] = Field(default_factory=list)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[datetime] = None


class Entity(BaseModel):
    entity_id: str
    entity_type: str
    risk_score: float = 0.0
    properties: dict[str, Any] = Field(default_factory=dict)
    connections: int = 0


class FraudRing(BaseModel):
    ring_id: str
    members: list[str] = Field(default_factory=list)
    total_amount: float = 0.0
    transaction_count: int = 0
    confidence: float = 0.0


class GraphSubgraph(BaseModel):
    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    status: str
    timestamp: float
