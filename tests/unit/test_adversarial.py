"""
Tests for Adversarial Feature Perturbation Detection.
"""

import pytest

from services.risk_engine.adversarial import (
    AdversarialDetector,
    PerturbationResult,
    EVASION_THRESHOLDS,
)


class TestThresholdProximity:
    def setup_method(self):
        self.detector = AdversarialDetector()

    def test_amount_just_below_ctr(self):
        result = self.detector.detect_perturbation(
            features={"amount": 9999.0}
        )
        assert result.manipulation_score > 0.5
        assert "amount" in result.suspicious_features
        assert any("$10,000" in e or "threshold" in e for e in result.evidence)

    def test_amount_well_below_ctr(self):
        result = self.detector.detect_perturbation(
            features={"amount": 5000.0}
        )
        assert result.manipulation_score < 0.6

    def test_normal_amount(self):
        result = self.detector.detect_perturbation(
            features={"amount": 150.0}
        )
        assert result.manipulation_score < 0.3
        assert result.is_adversarial is False

    def test_velocity_at_limit(self):
        result = self.detector.detect_perturbation(
            features={"transaction_velocity_1h": 9, "amount": 1000}
        )
        assert result.manipulation_score > 0.3


class TestPerturbationDetection:
    def setup_method(self):
        self.detector = AdversarialDetector()

    def test_structuring_pattern(self):
        # Classic structuring: $9,900 just below $10K
        result = self.detector.detect_perturbation(
            features={"amount": 9900.0}
        )
        assert result.manipulation_score > 0.4

    def test_legitimate_transaction(self):
        result = self.detector.detect_perturbation(
            features={"amount": 250.0, "transaction_velocity_1h": 1}
        )
        assert result.is_adversarial is False
        assert result.manipulation_score < 0.5

    def test_behavioral_inconsistency(self):
        # Current transaction is 10x the historical mean
        result = self.detector.detect_perturbation(
            features={"amount": 50000.0},
            history=[
                {"amount": 500.0},
                {"amount": 600.0},
                {"amount": 450.0},
            ],
        )
        assert result.manipulation_score > 0.3

    def test_no_history_no_consistency_check(self):
        result = self.detector.detect_perturbation(
            features={"amount": 50000.0},
            history=None,
        )
        # Still checks threshold proximity but not behavioral consistency
        assert isinstance(result.manipulation_score, float)


class TestBoundaryDistance:
    def setup_method(self):
        self.detector = AdversarialDetector()

    def test_high_risk_far_from_boundary(self):
        distance = self.detector.get_boundary_distance(
            features={"amount": 100000, "is_new_device": 1.0, "geo_velocity_anomaly": 1.0}
        )
        assert distance > 0.5

    def test_low_risk_far_from_boundary(self):
        distance = self.detector.get_boundary_distance(
            features={"amount": 50, "is_new_device": 0.0}
        )
        assert distance > 0.0

    def test_medium_risk_near_boundary(self):
        distance = self.detector.get_boundary_distance(
            features={"amount": 5000}
        )
        assert distance < 0.5


class TestFeatureSensitivity:
    def setup_method(self):
        self.detector = AdversarialDetector()

    def test_sensitivity_sums_to_one(self):
        sensitivities = self.detector.compute_feature_sensitivity(
            features={"amount": 15000, "is_new_device": 1.0, "transaction_velocity_1h": 5}
        )
        total = sum(sensitivities.values())
        assert abs(total - 1.0) < 0.01

    def test_amount_has_sensitivity(self):
        sensitivities = self.detector.compute_feature_sensitivity(
            features={"amount": 15000, "is_new_device": 0.0}
        )
        # Sensitivities are normalized to sum to 1.0, so if there are multiple features
        # each will have some portion
        assert "amount" in sensitivities

    def test_all_features_represented(self):
        features = {"amount": 1000, "velocity": 3, "device": 0.0}
        sensitivities = self.detector.compute_feature_sensitivity(features)
        assert set(sensitivities.keys()) == set(features.keys())


class TestPerturbationResult:
    def test_create_result(self):
        result = PerturbationResult(
            manipulation_score=0.75,
            boundary_distance=0.3,
            suspicious_features=["amount"],
            evidence=["Amount near CTR threshold"],
            is_adversarial=True,
        )
        assert result.is_adversarial is True
        assert result.manipulation_score == 0.75
