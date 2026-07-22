import hashlib
import json
import logging
from typing import Dict, Any, List
from .vector_store import VectorMemoryStore
from .knowledge_graph import FraudKnowledgeGraph
from .case_store import CaseStore
from core.schemas.investigation import InvestigationCase

logger = logging.getLogger(__name__)


class MemoryEngine:
    def __init__(self):
        self.vector_store = VectorMemoryStore()
        self.kg = FraudKnowledgeGraph()
        self.case_store = CaseStore()
        self._decisions: Dict[str, List[Any]] = {}

    def store_case(self, case: InvestigationCase) -> str:
        return self.case_store.create_case(case)

    def retrieve_case(self, case_id: str) -> InvestigationCase:
        return self.case_store.get_case(case_id)

    def search_similar_cases(self, features: Dict[str, Any], k: int = 5) -> List[InvestigationCase]:
        return self.case_store.search_cases(filters=features)

    def _text_to_embedding(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode()).hexdigest()
        return [int(digest[i:i+2], 16) / 255.0 for i in range(0, 64, 2)]

    def store_knowledge(self, entity: str, facts: Dict[str, Any]) -> None:
        text_repr = f"{entity}: {json.dumps(facts, default=str)}"
        embedding = self._text_to_embedding(text_repr)
        doc_id = hashlib.md5(text_repr.encode()).hexdigest()
        self.vector_store.store(doc_id, embedding, {"entity": entity, "facts": facts})
        self.kg.add_pattern(
            pattern_name=entity,
            description=json.dumps(facts, default=str)[:200],
            indicators=list(facts.keys()),
            fraud_type=facts.get("type", "Unknown")
        )

    def query_knowledge(self, query: str) -> List[Any]:
        embedding = self._text_to_embedding(query)
        results = self.vector_store.search(embedding, k=10)
        return [{"id": r[0], "score": r[1], "metadata": r[2]} for r in results]

    def store_decision(self, decision: Any) -> None:
        entity_id = decision.get("entity_id", "unknown") if isinstance(decision, dict) else "unknown"
        if entity_id not in self._decisions:
            self._decisions[entity_id] = []
        self._decisions[entity_id].append(decision)

    def get_decision_history(self, entity_id: str) -> List[Any]:
        return self._decisions.get(entity_id, [])
