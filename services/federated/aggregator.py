"""
Secure Federated Averaging Aggregator.

Aggregates weight updates from multiple AegisOS clients using
weighted FedAvg with anomaly detection on incoming updates.

Security features:
- Anomaly detection on weight deltas (reject outliers)
- Weighted average by number of local samples
- Convergence tracking across rounds
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.utils.logging import get_logger

logger = get_logger(__name__)

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class AggregationResult:
    """Result of a federated aggregation round."""

    global_weights: Dict[str, Any]
    clients_aggregated: int
    clients_rejected: int
    round_number: int
    convergence_metric: float


@dataclass
class ClientUpdate:
    """A weight update from a single federated client."""

    client_id: str
    weight_delta: Dict[str, Any]
    samples_trained: int
    metrics: Dict[str, float] = field(default_factory=dict)


class SecureFedAvgAggregator:
    """Federated Averaging with anomaly detection.

    Aggregation protocol:
    1. Collect weight deltas from all clients
    2. Reject anomalous updates (L2 norm > threshold)
    3. Weighted average by number of local samples
    4. Apply aggregated delta to global model
    5. Track convergence

    Usage:
        agg = SecureFedAvgAggregator(initial_weights)
        result = agg.aggregate([update1, update2, update3])
        # result.global_weights is the new global model
    """

    def __init__(
        self,
        initial_weights: Optional[Dict[str, Any]] = None,
        anomaly_threshold: float = 5.0,
    ):
        self._global_weights = initial_weights or {}
        self._anomaly_threshold = anomaly_threshold
        self._round_number = 0
        self._convergence_history: List[float] = []

    @property
    def global_weights(self) -> Dict[str, Any]:
        return self._global_weights

    @property
    def round_number(self) -> int:
        return self._round_number

    @property
    def convergence_history(self) -> List[float]:
        return self._convergence_history.copy()

    def aggregate(self, updates: List[ClientUpdate]) -> AggregationResult:
        """Aggregate client updates into new global model.

        Uses sample-weighted FedAvg with outlier rejection.
        """
        self._round_number += 1

        valid_updates, rejected = self._filter_anomalies(updates)

        if not valid_updates:
            logger.warning("No valid updates to aggregate", round=self._round_number)
            return AggregationResult(
                global_weights=self._global_weights,
                clients_aggregated=0,
                clients_rejected=len(rejected),
                round_number=self._round_number,
                convergence_metric=0.0,
            )

        aggregated_delta = self._weighted_average(valid_updates)

        self._apply_delta(aggregated_delta)

        convergence = self._compute_convergence(aggregated_delta)
        self._convergence_history.append(convergence)

        logger.info(
            "Aggregation complete",
            round=self._round_number,
            clients_aggregated=len(valid_updates),
            clients_rejected=len(rejected),
            convergence=f"{convergence:.6f}",
        )

        return AggregationResult(
            global_weights=self._global_weights,
            clients_aggregated=len(valid_updates),
            clients_rejected=len(rejected),
            round_number=self._round_number,
            convergence_metric=convergence,
        )

    def _filter_anomalies(
        self, updates: List[ClientUpdate]
    ) -> tuple:
        """Reject updates with anomalous L2 norms (possible poisoning attack)."""
        valid = []
        rejected = []

        norms = []
        for update in updates:
            norm = self._compute_update_norm(update.weight_delta)
            norms.append(norm)

        if not norms:
            return [], []

        if NUMPY_AVAILABLE and len(norms) > 2:
            median_norm = float(np.median(norms))
            mad = float(np.median(np.abs(np.array(norms) - median_norm)))
            threshold = median_norm + self._anomaly_threshold * max(mad, 0.01)
        else:
            sorted_norms = sorted(norms)
            median_norm = sorted_norms[len(sorted_norms) // 2]
            threshold = median_norm * (1 + self._anomaly_threshold)

        for update, norm in zip(updates, norms):
            if norm <= threshold:
                valid.append(update)
            else:
                rejected.append(update)
                logger.warning(
                    "Client update rejected (anomalous)",
                    client_id=update.client_id,
                    norm=f"{norm:.4f}",
                    threshold=f"{threshold:.4f}",
                )

        return valid, rejected

    def _weighted_average(self, updates: List[ClientUpdate]) -> Dict[str, Any]:
        """Compute sample-weighted average of weight deltas."""
        total_samples = sum(u.samples_trained for u in updates)
        if total_samples == 0:
            total_samples = len(updates)

        aggregated: Dict[str, Any] = {}

        for key in updates[0].weight_delta:
            values = []
            weights_for_key = []

            for update in updates:
                if key in update.weight_delta:
                    val = update.weight_delta[key]
                    weight = update.samples_trained / total_samples
                    values.append(val)
                    weights_for_key.append(weight)

            if not values:
                continue

            if NUMPY_AVAILABLE and hasattr(values[0], 'shape'):
                weighted_sum = sum(v * w for v, w in zip(values, weights_for_key))
                aggregated[key] = weighted_sum
            else:
                aggregated[key] = values[0]

        return aggregated

    def _apply_delta(self, delta: Dict[str, Any]):
        """Apply aggregated delta to global weights."""
        for key, val in delta.items():
            if key in self._global_weights:
                if NUMPY_AVAILABLE and hasattr(val, '__add__'):
                    self._global_weights[key] = self._global_weights[key] + val
                else:
                    self._global_weights[key] = val
            else:
                self._global_weights[key] = val

    def _compute_update_norm(self, delta: Dict[str, Any]) -> float:
        """Compute L2 norm of a weight delta."""
        if not NUMPY_AVAILABLE:
            return 1.0

        total_norm_sq = 0.0
        for val in delta.values():
            if hasattr(val, 'shape'):
                total_norm_sq += float(np.sum(val ** 2))
            elif isinstance(val, (int, float)):
                total_norm_sq += val ** 2

        return float(np.sqrt(total_norm_sq))

    def _compute_convergence(self, delta: Dict[str, Any]) -> float:
        """Compute convergence metric (smaller = more converged)."""
        return self._compute_update_norm(delta)
