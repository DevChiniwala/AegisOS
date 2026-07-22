"""
FastAPI Dependencies for Dependency Injection.
"""
from fastapi import Depends
from core.events import get_event_bus
from core.database.session import get_session

# Mock engine getters for now, these should be imported from their respective services
def get_feature_engine():
    pass

def get_risk_engine():
    pass

def get_graph_engine():
    pass

def get_behavioral_engine():
    pass

def get_investigation_orchestrator():
    pass

def get_memory_engine():
    pass

def get_explainability_engine():
    pass

def get_db():
    return get_session()
