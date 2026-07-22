import numpy as np
from typing import Dict, List, Tuple, Any

class VectorMemoryStore:
    def __init__(self):
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

    def store(self, id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        self.vectors[id] = np.array(embedding)
        self.metadata[id] = metadata

    def search(self, query_embedding: List[float], k: int = 10, filters: Dict[str, Any] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        if not self.vectors:
            return []
            
        q_vec = np.array(query_embedding)
        results = []
        
        for v_id, v in self.vectors.items():
            if filters:
                meta = self.metadata.get(v_id, {})
                if not all(meta.get(fk) == fv for fk, fv in filters.items()):
                    continue
                    
            sim = np.dot(q_vec, v) / (np.linalg.norm(q_vec) * np.linalg.norm(v))
            results.append((v_id, float(sim), self.metadata.get(v_id, {})))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def delete(self, id: str) -> None:
        if id in self.vectors:
            del self.vectors[id]
        if id in self.metadata:
            del self.metadata[id]
