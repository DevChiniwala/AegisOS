import math
from typing import Dict, List, Tuple
from models.base import FraudModel
from core.utils.logging import get_logger

logger = get_logger(__name__)


class AdaptiveEnsemble:
    def __init__(self, models: List[FraudModel]):
        self.models = models
        self._calibration_a = 1.0
        self._calibration_b = 0.0

    def fit_calibration(self, scores: List[float], labels: List[int]):
        """Fit Platt scaling parameters on validation scores and true labels."""
        if len(scores) < 10:
            return
        n_pos = sum(labels)
        n_neg = len(labels) - n_pos
        if n_pos == 0 or n_neg == 0:
            return

        target_hi = (n_pos + 1.0) / (n_pos + 2.0)
        target_lo = 1.0 / (n_neg + 2.0)
        targets = [target_hi if y == 1 else target_lo for y in labels]

        a, b = 0.0, math.log((n_neg + 1.0) / (n_pos + 1.0))
        for _ in range(100):
            d_a, d_b = 0.0, 0.0
            for s, t in zip(scores, targets):
                p = 1.0 / (1.0 + math.exp(-(a * s + b)))
                d = p - t
                d_a += d * s
                d_b += d
            a -= 0.01 * d_a / len(scores)
            b -= 0.01 * d_b / len(scores)

        self._calibration_a = a
        self._calibration_b = b

    def _compute_shap_agreement(self, features: Dict[str, float]) -> Dict[str, float]:
        if len(self.models) < 2:
            return {m.model_name: 1.0 for m in self.models}

        explanations = {}
        for model in self.models:
            shap_values = model.explain(features)
            if shap_values:
                explanations[model.model_name] = shap_values

        if len(explanations) < 2:
            return {m.model_name: 1.0 for m in self.models}

        feature_names = list(features.keys())
        model_names = list(explanations.keys())

        agreement_scores = {}
        for model_name in model_names:
            model_shap = explanations[model_name]
            other_shaps = [explanations[n] for n in model_names if n != model_name]

            similarities = []
            for other in other_shaps:
                vec_a = [model_shap.get(f, 0.0) for f in feature_names]
                vec_b = [other.get(f, 0.0) for f in feature_names]
                similarity = self._cosine_similarity(vec_a, vec_b)
                similarities.append(similarity)

            agreement_scores[model_name] = sum(similarities) / len(similarities) if similarities else 0.0

        for name in [m.model_name for m in self.models]:
            if name not in agreement_scores:
                agreement_scores[name] = 0.5

        return agreement_scores

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return max(0.0, (dot / (mag_a * mag_b) + 1.0) / 2.0)

    def _dynamic_weights(self, agreement_scores: Dict[str, float]) -> Dict[str, float]:
        total = sum(agreement_scores.values())
        if total == 0:
            return {name: 1.0 / len(agreement_scores) for name in agreement_scores}
        return {name: score / total for name, score in agreement_scores.items()}

    def _calibrate_probability(self, raw_score: float) -> float:
        # Platt scaling: sigmoid(a*x + b) where a,b are fit on validation data
        # Default parameters produce near-identity for well-calibrated models
        a = self._calibration_a
        b = self._calibration_b
        import math
        try:
            calibrated = 1.0 / (1.0 + math.exp(-(a * raw_score + b)))
        except OverflowError:
            calibrated = 0.0 if (a * raw_score + b) < 0 else 1.0
        return max(0.0, min(1.0, calibrated))

    def predict(self, features: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        if not self.models:
            return 0.0, {}

        try:
            agreement = self._compute_shap_agreement(features)
            weights = self._dynamic_weights(agreement)
        except Exception as e:
            logger.error(f"SHAP agreement failed: {e}")
            weights = {model.model_name: 1.0 / len(self.models) for model in self.models}

        final_score = 0.0
        for model in self.models:
            score = model.predict(features)
            final_score += score * weights.get(model.model_name, 0.0)

        return self._calibrate_probability(final_score), weights
