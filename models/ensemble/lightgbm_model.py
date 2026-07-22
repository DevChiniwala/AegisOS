import logging
import joblib
from typing import Dict, List, Any

try:
    import lightgbm as lgb
except ImportError:
    lgb = None

try:
    import shap
except ImportError:
    shap = None

logger = logging.getLogger(__name__)

class LightGBMFraudModel:
    def __init__(self):
        self._name = "lightgbm"
        self._version = "1.0.0"
        self.model = None
        if lgb:
            self.model = lgb.LGBMClassifier(
                is_unbalance=True,
                num_leaves=63,
                learning_rate=0.05
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
        if not self.model or not shap:
            return {}
        try:
            import numpy as np
            feature_names = list(features.keys())
            X = np.array([list(features.values())])
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            return dict(zip(feature_names, shap_values[0].tolist()))
        except Exception as e:
            logger.warning(f"SHAP explanation failed: {e}")
            return {}

    def train(self, X: Any, y: Any, **kwargs):
        if self.model:
            self.model.fit(X, y)
            
    def save(self, path: str):
        joblib.dump(self.model, path)
        
    def load(self, path: str):
        self.model = joblib.load(path)
