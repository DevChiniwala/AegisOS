from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import Field
from .base import BaseSchema


class RiskLevel(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CRITICAL = "CRITICAL"


class RiskVerdict(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"
    BLOCK = "BLOCK"


class RiskScore(BaseSchema):
    score: float = Field(ge=0.0, le=1.0)
    level: RiskLevel
    verdict: RiskVerdict
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str
    scored_at: datetime = Field(default_factory=datetime.utcnow)


class FeatureImportance(BaseSchema):
    feature_name: str
    value: Any
    importance: float
    direction: str  # e.g., "increases_risk", "decreases_risk"


class RiskExplanation(BaseSchema):
    risk_score: RiskScore
    top_features: List[FeatureImportance]
    shap_values: Dict[str, float]
    graph_evidence: List[Dict[str, Any]]
    behavioral_deviations: List[str]
    counterfactual: str
    natural_language_explanation: str
    similar_cases: List[Dict[str, Any]]
    rules_triggered: List[str]
