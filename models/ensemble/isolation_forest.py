import joblib
from typing import Dict, List, Any

try:
    from sklearn.ensemble import IsolationForest
    import numpy as np
except ImportError:
    IsolationForest = None
    np = None

class IsolationForestModel:
    def __init__(self):
        self._name = "isolation_forest"
        self._version = "1.0.0"
        self.model = None
        if IsolationForest:
            self.model = IsolationForest(
                n_estimators=200,
                contamination='auto',
                random_state=42
            )
            
    @property
    def model_name(self) -> str:
        return self._name
        
    @property
    def model_version(self) -> str:
        return self._version
        
    def predict(self, features: Dict[str, float]) -> float:
        if not self.model: return 0.5
        X = np.array([list(features.values())])
        score = self.model.decision_function(X)[0]
        prob = 1.0 - (1.0 / (1.0 + np.exp(-score)))
        return float(prob)
        
    def predict_batch(self, features: List[Dict[str, float]]) -> List[float]:
        if not self.model: return [0.5]*len(features)
        X = np.array([[f for f in feat.values()] for feat in features])
        scores = self.model.decision_function(X)
        probs = 1.0 - (1.0 / (1.0 + np.exp(-scores)))
        return probs.tolist()
        
    def explain(self, features: Dict[str, float]) -> Dict[str, float]:
        return {}
        
    def train(self, X: Any, y: Any, **kwargs):
        if self.model:
            self.model.fit(X)
            
    def save(self, path: str):
        joblib.dump(self.model, path)
        
    def load(self, path: str):
        self.model = joblib.load(path)
