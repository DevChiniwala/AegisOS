import numpy as np
from core.schemas.risk import FeatureImportance
from typing import Dict, List, Any
try:
    import shap
except ImportError:
    shap = None

class SHAPExplainer:
    def explain_prediction(self, model: Any, features: Dict[str, float]) -> Dict[str, float]:
        if not model:
            # Dummy values if no model provided
            return {k: v * 0.1 for k, v in features.items()}
            
        if shap is None:
            return {}
            
        feature_names = list(features.keys())
        feature_values = np.array([list(features.values())])
        
        try:
            # Try TreeExplainer first
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(feature_values)
        except Exception:
            # Fallback to KernelExplainer
            explainer = shap.KernelExplainer(model.predict, shap.kmeans(np.zeros((10, len(features))), 1))
            shap_values = explainer.shap_values(feature_values)
            
        # Format output
        values = shap_values[0] if isinstance(shap_values, list) else shap_values
        if len(values.shape) > 1:
            values = values[0]
            
        return dict(zip(feature_names, values))

    def top_features(self, shap_values: Dict[str, float], k: int = 10) -> List[FeatureImportance]:
        sorted_feats = sorted(shap_values.items(), key=lambda item: abs(item[1]), reverse=True)
        return [
            FeatureImportance(feature=k, importance=v, contribution="positive" if v > 0 else "negative")
            for k, v in sorted_feats[:k]
        ]

    def feature_interaction(self, shap_values: Dict[str, float]) -> Dict[str, float]:
        # Placeholder for actual SHAP interaction values which require shap.TreeExplainer(model).shap_interaction_values
        return {}
