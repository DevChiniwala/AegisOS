from typing import Dict, Any, List
from .vector_store import VectorMemoryStore
from .knowledge_graph import FraudKnowledgeGraph
from .case_store import CaseStore
from core.schemas.investigation import InvestigationCase

class MemoryEngine:
    def __init__(self):
        self.vector_store = VectorMemoryStore()
        self.kg = FraudKnowledgeGraph()
        self.case_store = CaseStore()

    def store_case(self, case: InvestigationCase) -> str:
        return self.case_store.create_case(case)

    def retrieve_case(self, case_id: str) -> InvestigationCase:
        return self.case_store.get_case(case_id)

    def search_similar_cases(self, features: Dict[str, Any], k: int = 5) -> List[InvestigationCase]:
        # Would normally use vector embedding of features
        return self.case_store.search_cases(filters=features)

    def store_knowledge(self, entity: str, facts: Dict[str, Any]) -> None:
        pass # Store in KG

    def query_knowledge(self, query: str) -> List[Any]:
        return []

    def store_decision(self, decision: Any) -> None:
        pass

    def get_decision_history(self, entity_id: str) -> List[Any]:
        return []
