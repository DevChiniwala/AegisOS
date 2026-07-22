import joblib
from typing import Dict, List, Any
from models.base import FraudModel

try:
    import xgboost as xgb
except ImportError:
    xgb = None

class XGBoostFraudModel:
    def __init__(self):
        self._name = "xgboost"
        self._version = "1.0.0"
        self.model = None
        if xgb:
            self.model = xgb.XGBClassifier(
                scale_pos_weight=10,
                max_depth=6,
                learning_rate=0.1,
                n_estimators=500
            )
            
    @property
    def model_name(self) -> str:
        return self._name
        
    @property
    def model_version(self) -> str:
        return self._version
        
    def predict(self, features: Dict[str, float]) -> float:
        if not self.model: return 0.5
        import numpy as np
        X = np.array([list(features.values())])
        return float(self.model.predict_proba(X)[0][1])
        
    def predict_batch(self, features: List[Dict[str, float]]) -> List[float]:
        if not self.model: return [0.5]*len(features)
        import numpy as np
        X = np.array([[f for f in feat.values()] for feat in features])
        return self.model.predict_proba(X)[:, 1].tolist()
        
    def explain(self, features: Dict[str, float]) -> Dict[str, float]:
        return {}
        
    def train(self, X: Any, y: Any, **kwargs):
        if self.model:
            self.model.fit(X, y)
            
    def save(self, path: str):
        joblib.dump(self.model, path)
        
    def load(self, path: str):
        self.model = joblib.load(path)
