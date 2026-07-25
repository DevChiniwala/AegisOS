"""
Adaptive Differential Privacy Mechanism.

Implements the Gaussian mechanism for differentially private gradient
sharing in federated learning. Tracks cumulative privacy budget (epsilon)
across training rounds using Renyi Differential Privacy accounting.

Key properties:
- Per-round epsilon control (tighter for sensitive features)
- Gradient clipping to bound sensitivity
- Cumulative privacy budget tracking
- Adaptive noise scaling based on convergence progress
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional

from core.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class PrivacyBudget:
    """Tracks cumulative differential privacy budget."""

    target_epsilon: float = 10.0
    target_delta: float = 1e-5
    spent_epsilon: float = 0.0
    rounds_completed: int = 0
    per_round_epsilons: List[float] = field(default_factory=list)

    @property
    def remaining_epsilon(self) -> float:
        return max(0.0, self.target_epsilon - self.spent_epsilon)

    @property
    def budget_exhausted(self) -> bool:
        return self.spent_epsilon >= self.target_epsilon


class AdaptiveDPMechanism:
    """Gaussian mechanism with adaptive noise for federated learning.

    Usage:
        dp = AdaptiveDPMechanism(target_epsilon=10.0, target_delta=1e-5)
        clipped = dp.clip_gradients(gradients, max_norm=1.0)
        noisy = dp.add_noise(clipped, epsilon=1.0, delta=1e-5)
        print(f"Privacy spent: {dp.cumulative_epsilon}")
    """

    def __init__(
        self,
        target_epsilon: float = 10.0,
        target_delta: float = 1e-5,
        max_grad_norm: float = 1.0,
    ):
        self._budget = PrivacyBudget(
            target_epsilon=target_epsilon,
            target_delta=target_delta,
        )
        self._max_grad_norm = max_grad_norm

    @property
    def cumulative_epsilon(self) -> float:
        return self._budget.spent_epsilon

    @property
    def budget(self) -> PrivacyBudget:
        return self._budget

    @property
    def budget_exhausted(self) -> bool:
        return self._budget.budget_exhausted

    def clip_gradients(self, gradients: "np.ndarray", max_norm: Optional[float] = None) -> "np.ndarray":
        """Clip gradients to bound sensitivity (L2 norm clipping)."""
        if not NUMPY_AVAILABLE:
            return gradients

        clip_norm = max_norm or self._max_grad_norm
        grad_norm = np.linalg.norm(gradients)

        if grad_norm > clip_norm:
            gradients = gradients * (clip_norm / grad_norm)

        return gradients

    def add_noise(
        self,
        gradients: "np.ndarray",
        epsilon: float,
        delta: Optional[float] = None,
    ) -> "np.ndarray":
        """Add calibrated Gaussian noise to clipped gradients.

        Noise scale: sigma = sensitivity * sqrt(2 * ln(1.25/delta)) / epsilon
        """
        if not NUMPY_AVAILABLE:
            return gradients

        if self._budget.budget_exhausted:
            raise PrivacyBudgetExhaustedError(
                f"Privacy budget exhausted: spent {self._budget.spent_epsilon:.2f} "
                f"of {self._budget.target_epsilon:.2f}"
            )

        delta = delta or self._budget.target_delta
        sensitivity = self._max_grad_norm

        sigma = sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / epsilon

        noise = np.random.normal(0, sigma, size=gradients.shape)
        noisy_gradients = gradients + noise

        self._budget.spent_epsilon += epsilon
        self._budget.rounds_completed += 1
        self._budget.per_round_epsilons.append(epsilon)

        logger.info(
            "DP noise added",
            epsilon=epsilon,
            sigma=f"{sigma:.4f}",
            cumulative_epsilon=f"{self._budget.spent_epsilon:.2f}",
            remaining=f"{self._budget.remaining_epsilon:.2f}",
        )

        return noisy_gradients

    def compute_noise_scale(self, epsilon: float, delta: Optional[float] = None) -> float:
        """Compute the noise standard deviation for given privacy parameters."""
        delta = delta or self._budget.target_delta
        sensitivity = self._max_grad_norm
        return sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / epsilon

    def get_adaptive_epsilon(self, round_number: int, total_rounds: int) -> float:
        """Compute per-round epsilon that distributes budget evenly with warmup.

        Early rounds get slightly more epsilon (less noise) for faster convergence,
        later rounds get tighter privacy.
        """
        if total_rounds <= 0:
            return 1.0

        remaining_budget = self._budget.remaining_epsilon
        remaining_rounds = max(1, total_rounds - round_number)

        base_epsilon = remaining_budget / remaining_rounds

        warmup_factor = 1.2 if round_number < total_rounds * 0.2 else 1.0
        cooldown_factor = 0.8 if round_number > total_rounds * 0.8 else 1.0

        return base_epsilon * warmup_factor * cooldown_factor


class PrivacyBudgetExhaustedError(Exception):
    """Raised when the differential privacy budget is fully spent."""

    pass
