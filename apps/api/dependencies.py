"""
FastAPI Dependencies for Dependency Injection.
"""
from fastapi import Request
from core.events import get_event_bus
from core.database.session import get_session
from services.feature_engine.engine import FeatureEngineeringEngine
from services.risk_engine.engine import RiskScoringEngine
from services.graph_engine.engine import GraphIntelligenceEngine
from services.graph_engine.store import NetworkXGraphStore
from services.behavioral_ai.engine import BehavioralIntelligenceEngine
from services.agents.orchestrator import InvestigationOrchestrator
from services.memory.engine import MemoryEngine
from services.explainability.engine import ExplainabilityEngine

_feature_engine = None
_risk_engine = None
_graph_engine = None
_behavioral_engine = None
_investigation_orchestrator = None
_memory_engine = None
_explainability_engine = None


def get_feature_engine() -> FeatureEngineeringEngine:
    global _feature_engine
    if _feature_engine is None:
        _feature_engine = FeatureEngineeringEngine()
    return _feature_engine


def get_risk_engine() -> RiskScoringEngine:
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskScoringEngine()
    return _risk_engine


def get_graph_engine() -> GraphIntelligenceEngine:
    global _graph_engine
    if _graph_engine is None:
        store = NetworkXGraphStore()
        _graph_engine = GraphIntelligenceEngine(store)
    return _graph_engine


def get_behavioral_engine() -> BehavioralIntelligenceEngine:
    global _behavioral_engine
    if _behavioral_engine is None:
        _behavioral_engine = BehavioralIntelligenceEngine()
    return _behavioral_engine


def get_investigation_orchestrator() -> InvestigationOrchestrator:
    global _investigation_orchestrator
    if _investigation_orchestrator is None:
        _investigation_orchestrator = InvestigationOrchestrator()
    return _investigation_orchestrator


def get_memory_engine() -> MemoryEngine:
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = MemoryEngine()
    return _memory_engine


def get_explainability_engine() -> ExplainabilityEngine:
    global _explainability_engine
    if _explainability_engine is None:
        _explainability_engine = ExplainabilityEngine()
    return _explainability_engine


def get_db():
    return get_session()
