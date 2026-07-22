import joblib
from typing import Dict, List, Any

try:
    from catboost import CatBoostClassifier
except ImportError:
    CatBoostClassifier = None

class CatBoostFraudModel:
    def __init__(self):
        self._name = "catboost"
        self._version = "1.0.0"
        self.model = None
        if CatBoostClassifier:
            self.model = CatBoostClassifier(
                auto_class_weights='Balanced',
                depth=8,
                iterations=1000,
                verbose=False
            )
            
    @property
    def model_name(self) -> str:
        return self._name
        
    @property
    def model_version(self) -> str:
        return self._version
        
    def predict(self, features: Dict[str, float]) -> float:
        if not self.model: return 0.5
        return float(self.model.predict_proba([list(features.values())])[0][1])
        
    def predict_batch(self, features: List[Dict[str, float]]) -> List[float]:
        if not self.model: return [0.5]*len(features)
        X = [[f for f in feat.values()] for feat in features]
        return self.model.predict_proba(X)[:, 1].tolist()
        
    def explain(self, features: Dict[str, float]) -> Dict[str, float]:
        return {}
        
    def train(self, X: Any, y: Any, **kwargs):
        if self.model:
            self.model.fit(X, y)
            
    def save(self, path: str):
        if self.model:
            self.model.save_model(path)
        
    def load(self, path: str):
        if self.model:
            self.model.load_model(path)
