from typing import Dict, List, Tuple
from models.base import FraudModel
from core.utils.logging import get_logger

logger = get_logger(__name__)

class AdaptiveEnsemble:
    def __init__(self, models: List[FraudModel]):
        self.models = models
        
    def _compute_shap_agreement(self, features: Dict[str, float]) -> Dict[str, float]:
        # Dummy implementation for SHAP agreement
        return {model.model_name: 1.0 for model in self.models}
        
    def _dynamic_weights(self, agreement_scores: Dict[str, float]) -> Dict[str, float]:
        total = sum(agreement_scores.values())
        if total == 0:
            return {name: 1.0/len(agreement_scores) for name in agreement_scores}
        return {name: score/total for name, score in agreement_scores.items()}
        
    def _calibrate_probability(self, raw_score: float) -> float:
        return raw_score
        
    def predict(self, features: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        if not self.models:
            return 0.0, {}
            
        try:
            agreement = self._compute_shap_agreement(features)
            weights = self._dynamic_weights(agreement)
        except Exception as e:
            logger.error(f"SHAP agreement failed: {e}")
            weights = {model.model_name: 1.0/len(self.models) for model in self.models}
            
        final_score = 0.0
        for model in self.models:
            score = model.predict(features)
            final_score += score * weights.get(model.model_name, 0.0)
            
        return self._calibrate_probability(final_score), weights
