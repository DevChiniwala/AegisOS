from typing import Dict, List, Any
import numpy as np

class SimilarCaseFinder:
    def __init__(self):
        # Mock database of past cases for demonstration
        self.history = [
            {"case_id": "C001", "features": {"amount": 5000, "velocity": 10}, "outcome": "fraud", "key_features": ["amount", "velocity"]},
            {"case_id": "C002", "features": {"amount": 50, "velocity": 1}, "outcome": "legitimate", "key_features": []},
            {"case_id": "C003", "features": {"amount": 4500, "velocity": 8}, "outcome": "fraud", "key_features": ["amount"]},
        ]

    def _cosine_sim(self, vec1: np.array, vec2: np.array) -> float:
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def find_similar(self, features: Dict[str, float], k: int = 5) -> List[Dict[str, Any]]:
        target_vec = np.array([features.get(k, 0) for k in ["amount", "velocity"]])
        
        similarities = []
        for case in self.history:
            case_vec = np.array([case["features"].get(k, 0) for k in ["amount", "velocity"]])
            sim = self._cosine_sim(target_vec, case_vec)
            similarities.append((sim, case))
            
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for sim, case in similarities[:k]:
            results.append({
                "case_id": case["case_id"],
                "similarity_score": sim,
                "outcome": case["outcome"],
                "key_features": case["key_features"]
            })
            
        return results
