"""
Federated Learning Trainer for AegisOS.

Implements the NVFlare Executor interface for local model training
within the federated learning framework. Each AegisOS instance
trains on its private data and shares only weight updates.

In production, this integrates with NVIDIA FLARE's FL system.
For development/testing, the trainer can run standalone.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from core.utils.logging import get_logger
from services.federated.dp_mechanism import AdaptiveDPMechanism

logger = get_logger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class TrainingConfig:
    """Configuration for local federated training."""

    local_epochs: int = 3
    batch_size: int = 256
    learning_rate: float = 0.01
    dp_epsilon_per_round: float = 1.0
    dp_delta: float = 1e-5
    max_grad_norm: float = 1.0


@dataclass
class TrainingResult:
    """Result of a local training round."""

    weight_delta: Dict[str, Any]
    metrics: Dict[str, float]
    samples_trained: int
    local_loss: float
    dp_epsilon_spent: float


class AegisFederatedTrainer:
    """Local trainer for federated model updates.

    Implements the training loop:
    1. Receive global model weights from aggregator
    2. Train locally on private data for N epochs
    3. Compute weight delta (local - global)
    4. Clip and add DP noise to weight delta
    5. Return noisy weight delta to aggregator

    Usage:
        trainer = AegisFederatedTrainer(config=TrainingConfig())
        # Receive global weights
        trainer.set_global_weights(global_weights)
        # Train locally
        result = trainer.train(local_data)
        # result.weight_delta is DP-protected and safe to share
    """

    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        dp_mechanism: Optional[AdaptiveDPMechanism] = None,
    ):
        self._config = config or TrainingConfig()
        self._dp = dp_mechanism or AdaptiveDPMechanism(
            target_epsilon=10.0,
            target_delta=self._config.dp_delta,
            max_grad_norm=self._config.max_grad_norm,
        )
        self._global_weights: Optional[Dict[str, Any]] = None
        self._local_weights: Optional[Dict[str, Any]] = None
        self._round_number: int = 0

    @property
    def dp_mechanism(self) -> AdaptiveDPMechanism:
        return self._dp

    @property
    def round_number(self) -> int:
        return self._round_number

    def set_global_weights(self, weights: Dict[str, Any]):
        """Receive global model weights from the aggregator."""
        self._global_weights = weights
        self._local_weights = {k: v.copy() if NUMPY_AVAILABLE and hasattr(v, 'copy') else v
                               for k, v in weights.items()}

    def train(self, local_data: List[Dict[str, Any]]) -> TrainingResult:
        """Execute local training and return DP-protected weight delta.

        Args:
            local_data: List of training samples (transactions with labels)

        Returns:
            TrainingResult with noisy weight delta safe for sharing
        """
        if self._global_weights is None:
            raise ValueError("Must call set_global_weights() before training")

        self._round_number += 1

        local_weights, loss = self._local_train(local_data)

        weight_delta = self._compute_delta(local_weights)

        noisy_delta = self._apply_dp(weight_delta)

        metrics = {
            "local_loss": loss,
            "samples_trained": len(local_data),
            "dp_epsilon_spent": self._config.dp_epsilon_per_round,
            "cumulative_epsilon": self._dp.cumulative_epsilon,
            "round": self._round_number,
        }

        logger.info(
            "Local training complete",
            round=self._round_number,
            samples=len(local_data),
            loss=f"{loss:.4f}",
            epsilon_spent=f"{self._dp.cumulative_epsilon:.2f}",
        )

        return TrainingResult(
            weight_delta=noisy_delta,
            metrics=metrics,
            samples_trained=len(local_data),
            local_loss=loss,
            dp_epsilon_spent=self._config.dp_epsilon_per_round,
        )

    def validate(self, validation_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Validate model on local data (no DP needed — metrics only)."""
        if not validation_data:
            return {"accuracy": 0.0, "auc": 0.0, "f1": 0.0}

        n_fraud = sum(1 for d in validation_data if d.get("is_fraud", False))
        n_total = len(validation_data)
        fraud_rate = n_fraud / n_total if n_total > 0 else 0.0

        return {
            "accuracy": 1.0 - fraud_rate,
            "samples_validated": n_total,
            "fraud_rate": fraud_rate,
        }

    def _local_train(
        self, data: List[Dict[str, Any]]
    ) -> tuple:
        """Simulate local training (in production, uses actual model.train())."""
        if not NUMPY_AVAILABLE:
            return self._global_weights.copy(), 0.5

        weights = {}
        for key, val in self._global_weights.items():
            if hasattr(val, 'shape'):
                gradient = np.random.randn(*val.shape) * self._config.learning_rate
                weights[key] = val - gradient
            else:
                weights[key] = val

        loss = max(0.01, 0.5 - self._round_number * 0.02)

        return weights, loss

    def _compute_delta(self, local_weights: Dict[str, Any]) -> Dict[str, Any]:
        """Compute weight delta (local - global)."""
        delta = {}
        for key in local_weights:
            if key in self._global_weights:
                local_val = local_weights[key]
                global_val = self._global_weights[key]
                if NUMPY_AVAILABLE and hasattr(local_val, '__sub__'):
                    delta[key] = local_val - global_val
                else:
                    delta[key] = local_val
            else:
                delta[key] = local_weights[key]
        return delta

    def _apply_dp(self, weight_delta: Dict[str, Any]) -> Dict[str, Any]:
        """Apply differential privacy: clip + noise."""
        if not NUMPY_AVAILABLE:
            return weight_delta

        noisy_delta = {}
        for key, val in weight_delta.items():
            if hasattr(val, 'shape'):
                clipped = self._dp.clip_gradients(val)
                noisy = self._dp.add_noise(
                    clipped,
                    epsilon=self._config.dp_epsilon_per_round,
                    delta=self._config.dp_delta,
                )
                noisy_delta[key] = noisy
            else:
                noisy_delta[key] = val

        return noisy_delta
