"""Tests for the rule engine eval() context fix."""
import pytest
from unittest.mock import MagicMock
from services.risk_engine.rules.rule_engine import RuleEngine, RuleResult


class TestRuleEngine:
    def setup_method(self):
        self.engine = RuleEngine()

    def test_rules_loaded(self):
        assert len(self.engine.rules) > 0

    def test_large_amount_rule_triggers(self):
        tx = MagicMock()
        tx.amount = 100000
        features = {
            'is_large_amount': 1.0,
            'amount_log': 11.5,
        }
        result = self.engine.evaluate(tx, features)
        assert result.triggered is True
        assert result.action == "BLOCK"

    def test_low_risk_allows(self):
        tx = MagicMock()
        tx.amount = 50
        features = {
            'is_large_amount': 0.0,
            'amount_log': 3.9,
            'amount_zscore': 0.1,
            'currency_is_foreign': 0.0,
            'is_round_amount': 0.0,
            'amount_to_avg_ratio': 1.0,
        }
        result = self.engine.evaluate(tx, features)
        assert result.triggered is False
        assert result.action == "ALLOW"

    def test_features_accessible_as_dict_in_condition(self):
        """Verify that features.get() works inside eval context."""
        self.engine.rules = [{
            'name': 'test_rule',
            'action': 'FLAG',
            'condition': "features.get('test_key', 0.0) > 0.5",
            'reason': 'Test triggered'
        }]
        tx = MagicMock()
        features = {'test_key': 0.9}
        result = self.engine.evaluate(tx, features)
        assert result.triggered is True
        assert result.rule_name == 'test_rule'

    def test_missing_feature_uses_default(self):
        """features.get() with default should not raise."""
        self.engine.rules = [{
            'name': 'missing_key_rule',
            'action': 'FLAG',
            'condition': "features.get('nonexistent', 0.0) > 0.5",
            'reason': 'Should not trigger'
        }]
        tx = MagicMock()
        features = {}
        result = self.engine.evaluate(tx, features)
        assert result.triggered is False
