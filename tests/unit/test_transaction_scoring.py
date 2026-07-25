"""
End-to-end test for the transaction scoring pipeline.
Verifies: FeatureEngine -> RiskScoringEngine -> ScoringResult
"""
from unittest.mock import MagicMock

from core.schemas.risk import RiskLevel, RiskVerdict
from models.base import ModelRegistry
from services.feature_engine.engine import FeatureEngineeringEngine
from services.risk_engine.engine import RiskScoringEngine, ScoringResult


class TestScoringPipeline:
    def setup_method(self):
        self.feature_engine = FeatureEngineeringEngine()
        registry = ModelRegistry()
        registry.register_defaults()
        models = list(registry._models.values())
        self.risk_engine = RiskScoringEngine(models)

    def _make_transaction(self, amount=100.0, currency="USD"):
        tx = MagicMock()
        tx.amount = amount
        tx.currency = currency
        tx.type = "PURCHASE"
        tx.timestamp = None
        tx.sender_id = "user_123"
        tx.receiver_id = "merchant_456"
        tx.channel = "web"
        tx.transaction_type = "purchase"
        tx.latitude = None
        tx.longitude = None
        tx.device_id = None
        tx.ip_address = None
        return tx

    def test_low_amount_returns_low_risk(self):
        tx = self._make_transaction(amount=25.0)
        features = self.feature_engine.extract_features(
            transaction=tx, user=None, merchant=None, device=None, history=[]
        )
        result = self.risk_engine.score_transaction(tx, features)

        assert isinstance(result, ScoringResult)
        assert result.score >= 0.0
        assert result.score <= 1.0
        assert result.level in [RiskLevel.LOW, RiskLevel.MEDIUM]

    def test_scoring_result_has_required_fields(self):
        tx = self._make_transaction(amount=500.0)
        features = self.feature_engine.extract_features(
            transaction=tx, user=None, merchant=None, device=None, history=[]
        )
        result = self.risk_engine.score_transaction(tx, features)

        assert hasattr(result, "score")
        assert hasattr(result, "level")
        assert hasattr(result, "verdict")
        assert hasattr(result, "reasons")
        assert hasattr(result, "model_weights")
        assert hasattr(result, "latency_ms")
        assert result.latency_ms >= 0

    def test_rule_engine_blocks_impossible_travel(self):
        tx = self._make_transaction(amount=100.0)
        features = {"is_impossible_travel": 1.0}
        result = self.risk_engine.score_transaction(tx, features)

        assert result.verdict == RiskVerdict.BLOCK
        assert result.level == RiskLevel.CRITICAL
        assert any("impossible_travel" in r for r in result.reasons)

    def test_rule_engine_blocks_large_amount(self):
        tx = self._make_transaction(amount=100000.0)
        features = {"is_large_amount": 1.0, "amount_log": 11.5}
        result = self.risk_engine.score_transaction(tx, features)

        assert result.verdict == RiskVerdict.BLOCK
        assert result.level == RiskLevel.CRITICAL

    def test_feature_extraction_produces_features(self):
        tx = self._make_transaction(amount=250.0)
        features = self.feature_engine.extract_features(
            transaction=tx, user=None, merchant=None, device=None, history=[]
        )

        assert isinstance(features, dict)
        assert len(features) > 0
        assert "amount_log" in features

    def test_emulator_detected_blocks(self):
        tx = self._make_transaction()
        features = {"is_emulator": 1.0}
        result = self.risk_engine.score_transaction(tx, features)

        assert result.verdict == RiskVerdict.BLOCK
        assert "emulator_detected" in result.reasons[0]
