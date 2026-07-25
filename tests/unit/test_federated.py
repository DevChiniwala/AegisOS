"""
Tests for Federated AML Learning with Differential Privacy.

Tests DP mechanism, trainer, and aggregator components
without requiring NVIDIA FLARE (tests standalone logic).
"""

import numpy as np
import pytest

from services.federated.aggregator import (
    ClientUpdate,
    SecureFedAvgAggregator,
)
from services.federated.dp_mechanism import (
    AdaptiveDPMechanism,
    PrivacyBudget,
    PrivacyBudgetExhaustedError,
)
from services.federated.trainer import (
    AegisFederatedTrainer,
    TrainingConfig,
    TrainingResult,
)


class TestPrivacyBudget:
    def test_initial_budget(self):
        budget = PrivacyBudget(target_epsilon=10.0, target_delta=1e-5)
        assert budget.remaining_epsilon == 10.0
        assert budget.budget_exhausted is False
        assert budget.rounds_completed == 0

    def test_spending_budget(self):
        budget = PrivacyBudget(target_epsilon=10.0)
        budget.spent_epsilon = 5.0
        assert budget.remaining_epsilon == 5.0
        assert budget.budget_exhausted is False

    def test_exhausted_budget(self):
        budget = PrivacyBudget(target_epsilon=10.0)
        budget.spent_epsilon = 10.0
        assert budget.remaining_epsilon == 0.0
        assert budget.budget_exhausted is True


class TestAdaptiveDPMechanism:
    def setup_method(self):
        self.dp = AdaptiveDPMechanism(
            target_epsilon=10.0, target_delta=1e-5, max_grad_norm=1.0
        )

    def test_initial_state(self):
        assert self.dp.cumulative_epsilon == 0.0
        assert self.dp.budget_exhausted is False

    def test_clip_gradients_within_norm(self):
        gradients = np.array([0.3, 0.4])  # norm = 0.5
        clipped = self.dp.clip_gradients(gradients, max_norm=1.0)
        np.testing.assert_array_almost_equal(clipped, gradients)

    def test_clip_gradients_exceeds_norm(self):
        gradients = np.array([3.0, 4.0])  # norm = 5.0
        clipped = self.dp.clip_gradients(gradients, max_norm=1.0)
        assert np.linalg.norm(clipped) <= 1.01  # within tolerance

    def test_add_noise_changes_values(self):
        np.random.seed(42)
        gradients = np.array([0.5, 0.5, 0.5])
        noisy = self.dp.add_noise(gradients, epsilon=1.0)
        assert not np.allclose(noisy, gradients)

    def test_add_noise_tracks_epsilon(self):
        gradients = np.ones(10)
        self.dp.add_noise(gradients, epsilon=2.0)
        assert self.dp.cumulative_epsilon == 2.0
        self.dp.add_noise(gradients, epsilon=3.0)
        assert self.dp.cumulative_epsilon == 5.0

    def test_budget_exhaustion_raises(self):
        dp = AdaptiveDPMechanism(target_epsilon=2.0, max_grad_norm=1.0)
        gradients = np.ones(5)
        dp.add_noise(gradients, epsilon=2.0)  # spends full budget
        with pytest.raises(PrivacyBudgetExhaustedError):
            dp.add_noise(gradients, epsilon=1.0)

    def test_compute_noise_scale(self):
        sigma = self.dp.compute_noise_scale(epsilon=1.0, delta=1e-5)
        assert sigma > 0
        # Higher epsilon -> less noise
        sigma_high = self.dp.compute_noise_scale(epsilon=10.0, delta=1e-5)
        assert sigma_high < sigma

    def test_adaptive_epsilon(self):
        eps = self.dp.get_adaptive_epsilon(round_number=0, total_rounds=10)
        assert eps > 0
        # All per-round epsilons should be positive
        eps_mid = self.dp.get_adaptive_epsilon(round_number=5, total_rounds=10)
        assert eps_mid > 0


class TestAegisFederatedTrainer:
    def setup_method(self):
        self.config = TrainingConfig(
            local_epochs=2,
            batch_size=32,
            learning_rate=0.01,
            dp_epsilon_per_round=1.0,
        )
        self.trainer = AegisFederatedTrainer(config=self.config)

    def test_initial_state(self):
        assert self.trainer.round_number == 0
        assert self.trainer.dp_mechanism.cumulative_epsilon == 0.0

    def test_set_global_weights(self):
        weights = {"layer1": np.ones(10), "layer2": np.zeros(5)}
        self.trainer.set_global_weights(weights)
        # Should not raise

    def test_train_requires_global_weights(self):
        with pytest.raises(ValueError):
            self.trainer.train([{"amount": 100}])

    def test_train_returns_result(self):
        weights = {"layer1": np.ones(10), "bias1": np.zeros(5)}
        self.trainer.set_global_weights(weights)

        data = [{"amount": 100 + i, "is_fraud": i % 10 == 0} for i in range(50)]
        result = self.trainer.train(data)

        assert isinstance(result, TrainingResult)
        assert result.samples_trained == 50
        assert result.local_loss > 0
        assert result.dp_epsilon_spent == 1.0

    def test_train_increments_round(self):
        weights = {"layer1": np.ones(5)}
        self.trainer.set_global_weights(weights)
        self.trainer.train([{"x": 1}] * 10)
        assert self.trainer.round_number == 1
        self.trainer.train([{"x": 1}] * 10)
        assert self.trainer.round_number == 2

    def test_train_weight_delta_is_noisy(self):
        np.random.seed(42)
        weights = {"layer1": np.zeros(20)}
        self.trainer.set_global_weights(weights)
        result = self.trainer.train([{"x": 1}] * 10)
        # Delta should not be all zeros (noise + gradient)
        assert not np.allclose(result.weight_delta["layer1"], 0.0)

    def test_validate(self):
        metrics = self.trainer.validate([
            {"is_fraud": True},
            {"is_fraud": False},
            {"is_fraud": False},
            {"is_fraud": False},
        ])
        assert metrics["fraud_rate"] == 0.25
        assert metrics["samples_validated"] == 4

    def test_validate_empty(self):
        metrics = self.trainer.validate([])
        assert metrics["accuracy"] == 0.0


class TestSecureFedAvgAggregator:
    def setup_method(self):
        self.initial_weights = {
            "layer1": np.zeros(10),
            "layer2": np.zeros(5),
        }
        self.agg = SecureFedAvgAggregator(
            initial_weights=self.initial_weights,
            anomaly_threshold=3.0,
        )

    def test_initial_state(self):
        assert self.agg.round_number == 0
        assert len(self.agg.convergence_history) == 0

    def test_aggregate_single_client(self):
        update = ClientUpdate(
            client_id="client_1",
            weight_delta={"layer1": np.ones(10) * 0.1, "layer2": np.ones(5) * 0.05},
            samples_trained=100,
        )
        result = self.agg.aggregate([update])
        assert result.clients_aggregated == 1
        assert result.clients_rejected == 0
        assert result.round_number == 1

    def test_aggregate_multiple_clients(self):
        updates = [
            ClientUpdate(
                client_id=f"client_{i}",
                weight_delta={"layer1": np.ones(10) * 0.1 * (i + 1)},
                samples_trained=100 * (i + 1),
            )
            for i in range(3)
        ]
        result = self.agg.aggregate(updates)
        assert result.clients_aggregated == 3
        assert result.clients_rejected == 0

    def test_anomaly_rejection(self):
        normal_updates = [
            ClientUpdate(
                client_id=f"normal_{i}",
                weight_delta={"layer1": np.ones(10) * 0.1},
                samples_trained=100,
            )
            for i in range(5)
        ]
        anomalous = ClientUpdate(
            client_id="attacker",
            weight_delta={"layer1": np.ones(10) * 1000.0},  # extreme outlier
            samples_trained=100,
        )
        result = self.agg.aggregate(normal_updates + [anomalous])
        assert result.clients_rejected >= 1
        assert result.clients_aggregated <= 5

    def test_weighted_average(self):
        # Client with more samples should have more influence
        update_small = ClientUpdate(
            client_id="small",
            weight_delta={"layer1": np.ones(10) * 0.0},
            samples_trained=10,
        )
        update_large = ClientUpdate(
            client_id="large",
            weight_delta={"layer1": np.ones(10) * 1.0},
            samples_trained=990,
        )
        result = self.agg.aggregate([update_small, update_large])
        # Global weights should be closer to large client's delta
        layer1 = result.global_weights["layer1"]
        assert np.mean(layer1) > 0.9  # heavily weighted toward large client

    def test_convergence_tracking(self):
        for i in range(3):
            update = ClientUpdate(
                client_id="c1",
                weight_delta={"layer1": np.ones(10) * (0.1 / (i + 1))},
                samples_trained=100,
            )
            self.agg.aggregate([update])

        assert len(self.agg.convergence_history) == 3
        # Convergence should decrease (smaller updates)
        assert self.agg.convergence_history[-1] < self.agg.convergence_history[0]

    def test_empty_updates(self):
        result = self.agg.aggregate([])
        assert result.clients_aggregated == 0
        assert result.global_weights == self.initial_weights
