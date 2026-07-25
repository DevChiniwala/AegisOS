"""
Adversarial Feature Perturbation Detection.

Detects when an attacker manipulates transaction features to evade
the fraud detection model. Instead of just detecting fraud, detects
the PERTURBATION ITSELF as a signal.

Techniques:
- Feature sensitivity analysis (which features change the prediction most)
- Distribution-based anomaly detection (features look "unnatural")
- Boundary proximity scoring (how close to decision boundary)
- Structuring pattern detection (amounts just below thresholds)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import math

from core.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class PerturbationResult:
    """Result of adversarial perturbation detection."""

    manipulation_score: float
    boundary_distance: float
    suspicious_features: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    is_adversarial: bool = False


# Known threshold values that attackers try to stay below
EVASION_THRESHOLDS = {
    "amount": [10000.0, 5000.0, 3000.0],  # CTR, reporting, monitoring
    "transaction_velocity_1h": [10, 20],
    "transaction_velocity_24h": [50, 100],
}

# Features that are commonly perturbed by adversaries
PERTURBATION_SENSITIVE_FEATURES = {
    "amount", "transaction_velocity_1h", "transaction_velocity_24h",
    "amount_to_max_ratio", "time_since_last_transaction",
}


class AdversarialDetector:
    """Detect adversarial feature manipulation in transactions.

    Usage:
        detector = AdversarialDetector()
        result = detector.detect_perturbation(features, history)
        if result.is_adversarial:
            print(f"Manipulation detected: {result.evidence}")
    """

    def __init__(
        self,
        threshold_proximity_factor: float = 0.05,
        min_manipulation_score: float = 0.6,
    ):
        self._threshold_proximity = threshold_proximity_factor
        self._min_score = min_manipulation_score

    def detect_perturbation(
        self,
        features: Dict[str, float],
        history: Optional[List[Dict[str, float]]] = None,
    ) -> PerturbationResult:
        """Detect adversarial perturbation in transaction features.

        Combines multiple signals:
        1. Threshold proximity (amounts just below reporting limits)
        2. Feature distribution anomaly (unnatural precision)
        3. Behavioral inconsistency (sudden change in patterns)
        """
        scores = []
        evidence = []
        suspicious_features = []

        threshold_score, thresh_evidence = self._check_threshold_proximity(features)
        scores.append(threshold_score)
        evidence.extend(thresh_evidence)
        if threshold_score > 0.5:
            suspicious_features.append("amount")

        precision_score, prec_evidence = self._check_unnatural_precision(features)
        scores.append(precision_score)
        evidence.extend(prec_evidence)

        if history:
            consistency_score, cons_evidence = self._check_behavioral_consistency(
                features, history
            )
            scores.append(consistency_score)
            evidence.extend(cons_evidence)
            if consistency_score > 0.5:
                suspicious_features.extend(
                    [f for f in PERTURBATION_SENSITIVE_FEATURES if f in features]
                )

        if not scores:
            return PerturbationResult(
                manipulation_score=0.0, boundary_distance=1.0
            )

        manipulation_score = max(scores) * 0.6 + (sum(scores) / len(scores)) * 0.4

        boundary_distance = self._compute_boundary_distance(features)

        is_adversarial = manipulation_score >= self._min_score

        if is_adversarial:
            logger.warning(
                "Adversarial perturbation detected",
                score=f"{manipulation_score:.2f}",
                suspicious_features=suspicious_features,
            )

        return PerturbationResult(
            manipulation_score=manipulation_score,
            boundary_distance=boundary_distance,
            suspicious_features=list(set(suspicious_features)),
            evidence=evidence,
            is_adversarial=is_adversarial,
        )

    def compute_feature_sensitivity(
        self,
        features: Dict[str, float],
    ) -> Dict[str, float]:
        """Compute which features, if perturbed, change the risk most.

        Uses finite-difference approximation of the gradient.
        Higher sensitivity = attacker would target this feature.
        """
        sensitivities = {}
        base_risk = self._estimate_risk(features)

        for feature_name, value in features.items():
            if value == 0:
                perturbed_value = 0.01
            else:
                perturbed_value = value * 1.01

            perturbed_features = {**features, feature_name: perturbed_value}
            perturbed_risk = self._estimate_risk(perturbed_features)

            delta = abs(perturbed_risk - base_risk) / max(abs(value) * 0.01, 0.001)
            sensitivities[feature_name] = delta

        total = sum(sensitivities.values()) or 1.0
        return {k: v / total for k, v in sensitivities.items()}

    def get_boundary_distance(self, features: Dict[str, float]) -> float:
        """Compute distance from the decision boundary."""
        return self._compute_boundary_distance(features)

    def _check_threshold_proximity(
        self, features: Dict[str, float]
    ) -> tuple:
        """Check if features are suspiciously close to known thresholds."""
        score = 0.0
        evidence = []

        amount = features.get("amount", 0)
        for threshold in EVASION_THRESHOLDS.get("amount", []):
            if 0 < amount < threshold:
                relative_closeness = amount / threshold
                if relative_closeness > 0.9:
                    this_score = (relative_closeness - 0.9) / 0.1  # 0→1 as 90%→100%
                    score = max(score, this_score)
                    evidence.append(
                        f"Amount ${amount:,.2f} is {(1-relative_closeness)*100:.1f}% "
                        f"below ${threshold:,.0f} threshold"
                    )

        velocity_1h = features.get("transaction_velocity_1h", 0)
        for limit in EVASION_THRESHOLDS.get("transaction_velocity_1h", []):
            if velocity_1h == limit - 1:
                score = max(score, 0.7)
                evidence.append(f"Velocity {velocity_1h}/hr is exactly 1 below limit {limit}")

        return score, evidence

    def _check_unnatural_precision(
        self, features: Dict[str, float]
    ) -> tuple:
        """Detect unnaturally precise values (sign of deliberate manipulation)."""
        score = 0.0
        evidence = []

        amount = features.get("amount", 0)
        if amount > 0:
            str_amount = f"{amount:.2f}"
            if str_amount.endswith("99.00") or str_amount.endswith("99.99"):
                score = max(score, 0.6)
                evidence.append(f"Amount ${amount} has evasion-typical precision (.99)")

            if amount > 1000 and amount == int(amount) and int(amount) % 100 == 0:
                pass
            elif 9000 < amount < 10000 and (amount * 100) % 100 == 0:
                score = max(score, 0.5)
                evidence.append(f"Whole-dollar amount ${amount:.0f} near CTR threshold")

        return score, evidence

    def _check_behavioral_consistency(
        self, features: Dict[str, float], history: List[Dict[str, float]]
    ) -> tuple:
        """Check if current features are consistent with historical pattern."""
        if not history:
            return 0.0, []

        score = 0.0
        evidence = []

        current_amount = features.get("amount", 0)
        historical_amounts = [h.get("amount", 0) for h in history if "amount" in h]

        if historical_amounts and current_amount > 0:
            mean_amount = sum(historical_amounts) / len(historical_amounts)
            if mean_amount > 0:
                ratio = current_amount / mean_amount
                if 0.85 < ratio < 1.15 and current_amount > 5000:
                    pass
                elif ratio > 5.0:
                    score = max(score, 0.6)
                    evidence.append(
                        f"Amount {ratio:.1f}x historical mean — possible manipulation"
                    )

        return score, evidence

    def _compute_boundary_distance(self, features: Dict[str, float]) -> float:
        """Estimate distance from decision boundary (0 = on boundary, 1 = far)."""
        risk = self._estimate_risk(features)
        return abs(2 * risk - 1.0)

    def _estimate_risk(self, features: Dict[str, float]) -> float:
        """Simple risk estimation for sensitivity analysis."""
        risk = 0.3

        amount = features.get("amount", 0)
        if amount > 50000:
            risk += 0.3
        elif amount > 10000:
            risk += 0.2
        elif amount > 5000:
            risk += 0.1
        elif amount > 1000:
            risk += 0.05

        if features.get("is_new_device", 0) == 1.0:
            risk += 0.1
        if features.get("geo_velocity_anomaly", 0) > 0:
            risk += 0.15

        velocity = features.get("transaction_velocity_1h", 0)
        if velocity > 10:
            risk += 0.1
        elif velocity > 5:
            risk += 0.05

        return min(1.0, max(0.0, risk))
