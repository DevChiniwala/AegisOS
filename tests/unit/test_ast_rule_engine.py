"""
Tests for the safe AST-based expression evaluator in the rule engine.
Verifies that valid rule conditions pass while malicious expressions are rejected.
"""
import pytest
from services.risk_engine.rules.rule_engine import (
    SafeExpressionEvaluator,
    UnsafeExpressionError,
    RuleEngine,
)


class TestSafeExpressionEvaluator:
    def setup_method(self):
        self.features = {
            "amount_log": 5.5,
            "is_large_amount": 1.0,
            "transactions_last_1min": 3.0,
            "is_new_device": 0.0,
            "is_impossible_travel": 0.0,
            "unique_countries_24h": 1.0,
        }
        self.context = {"features": self.features, "transaction": {"amount": 500}}

    def test_simple_comparison(self):
        evaluator = SafeExpressionEvaluator(self.context)
        assert evaluator.evaluate("features.get('amount_log', 0) > 4.5") is True
        assert evaluator.evaluate("features.get('amount_log', 0) > 10.0") is False

    def test_equality(self):
        evaluator = SafeExpressionEvaluator(self.context)
        assert evaluator.evaluate("features.get('is_large_amount', 0.0) == 1.0") is True
        assert evaluator.evaluate("features.get('is_large_amount', 0.0) == 0.0") is False

    def test_boolean_and(self):
        evaluator = SafeExpressionEvaluator(self.context)
        result = evaluator.evaluate(
            "features.get('is_new_device', 0.0) == 1.0 and features.get('amount_log', 0) > 6.9"
        )
        assert result is False

    def test_boolean_or(self):
        evaluator = SafeExpressionEvaluator(self.context)
        result = evaluator.evaluate(
            "features.get('is_large_amount', 0.0) == 1.0 or features.get('amount_log', 0) > 10.8"
        )
        assert result is True

    def test_default_value_on_missing_key(self):
        evaluator = SafeExpressionEvaluator(self.context)
        assert evaluator.evaluate("features.get('nonexistent_key', 0.0) == 0.0") is True

    def test_rejects_import(self):
        evaluator = SafeExpressionEvaluator(self.context)
        with pytest.raises(UnsafeExpressionError):
            evaluator.evaluate("__import__('os').system('rm -rf /')")

    def test_rejects_dunder_access(self):
        evaluator = SafeExpressionEvaluator(self.context)
        with pytest.raises(UnsafeExpressionError):
            evaluator.evaluate("features.__class__.__mro__[1].__subclasses__()")

    def test_rejects_exec(self):
        evaluator = SafeExpressionEvaluator(self.context)
        with pytest.raises(UnsafeExpressionError):
            evaluator.evaluate("exec('import os')")

    def test_rejects_lambda(self):
        evaluator = SafeExpressionEvaluator(self.context)
        with pytest.raises(UnsafeExpressionError):
            evaluator.evaluate("(lambda: features)()")

    def test_rejects_comprehension(self):
        evaluator = SafeExpressionEvaluator(self.context)
        with pytest.raises(UnsafeExpressionError):
            evaluator.evaluate("[x for x in features]")

    def test_arithmetic(self):
        evaluator = SafeExpressionEvaluator(self.context)
        assert evaluator.evaluate("features.get('amount_log', 0) + 1 > 5") is True

    def test_unary_not(self):
        evaluator = SafeExpressionEvaluator(self.context)
        assert evaluator.evaluate("not features.get('is_impossible_travel', 0.0) == 1.0") is True


class TestRuleEngineIntegration:
    def test_rules_load(self):
        engine = RuleEngine()
        assert len(engine.rules) > 0

    def test_large_amount_triggers_block(self):
        engine = RuleEngine()
        from unittest.mock import MagicMock
        tx = MagicMock()
        features = {"is_large_amount": 1.0, "amount_log": 11.0}
        result = engine.evaluate(tx, features)
        assert result.triggered is True
        assert result.action == "BLOCK"

    def test_low_risk_passes(self):
        engine = RuleEngine()
        from unittest.mock import MagicMock
        tx = MagicMock()
        features = {
            "is_large_amount": 0.0,
            "amount_log": 3.0,
            "transactions_last_1min": 1.0,
            "transactions_last_1hour": 5.0,
            "is_impossible_travel": 0.0,
            "is_new_device": 0.0,
            "is_night": 0.0,
            "country_risk_score": 0.1,
            "is_round_amount": 0.0,
            "count_5m": 0.0,
            "is_emulator": 0.0,
            "unique_countries_24h": 1.0,
        }
        result = engine.evaluate(tx, features)
        assert result.triggered is False
        assert result.action == "ALLOW"
