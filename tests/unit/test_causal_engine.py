"""
Tests for the Causal Inference Risk Scoring Engine.

Tests DAG structure, causal path detection, feature weight computation,
and effect estimation (DAG-based fallback without DoWhy).
"""

import pytest

from services.risk_engine.causal.dag import FinancialCausalDAG, CausalEdge
from services.risk_engine.causal.engine import CausalRiskEngine, CausalEffect, CausalWeights


class TestFinancialCausalDAG:
    def setup_method(self):
        self.dag = FinancialCausalDAG()

    def test_dag_has_nodes(self):
        assert len(self.dag.nodes) > 10

    def test_dag_has_edges(self):
        assert self.dag.edge_count > 15

    def test_fraud_has_causes(self):
        causes = self.dag.get_causes_of("is_fraud")
        assert "account_compromised" in causes
        assert "structuring_intent" in causes
        assert "layering_intent" in causes

    def test_account_compromised_effects(self):
        effects = self.dag.get_effects_of("account_compromised")
        assert "is_fraud" in effects
        assert "is_new_device" in effects
        assert "geo_velocity_anomaly" in effects

    def test_causal_path_exists(self):
        assert self.dag.is_causal_path("account_compromised", "is_fraud") is True
        assert self.dag.is_causal_path("structuring_intent", "is_fraud") is True

    def test_no_causal_path(self):
        assert self.dag.is_causal_path("is_fraud", "account_compromised") is False
        assert self.dag.is_causal_path("is_new_device", "is_fraud") is False

    def test_confounders(self):
        confounders = self.dag.get_confounders("is_new_device", "is_fraud")
        assert "account_compromised" in confounders

    def test_no_confounders_for_direct_cause(self):
        confounders = self.dag.get_confounders("account_compromised", "is_fraud")
        assert len(confounders) == 0

    def test_propose_valid_edge(self):
        result = self.dag.propose_edge(
            "money_mule_network", "is_fraud", "mule accounts enable cash-out"
        )
        assert result is True
        assert self.dag.is_causal_path("money_mule_network", "is_fraud")

    def test_reject_cycle_edge(self):
        result = self.dag.propose_edge("is_fraud", "account_compromised")
        assert result is False

    def test_reject_self_edge(self):
        result = self.dag.propose_edge("is_fraud", "is_fraud")
        assert result is False

    def test_reject_observable_causes_latent(self):
        result = self.dag.propose_edge("is_new_device", "account_compromised")
        assert result is False

    def test_reject_fraud_as_cause(self):
        result = self.dag.propose_edge("is_fraud", "some_feature")
        assert result is False

    def test_to_gml(self):
        gml = self.dag.to_gml()
        assert "graph [directed 1" in gml
        assert "node" in gml
        assert "edge" in gml
        assert "account_compromised" in gml

    def test_to_dot(self):
        dot = self.dag.to_dot()
        assert "digraph" in dot
        assert "->" in dot


class TestCausalEffect:
    def test_create_effect(self):
        effect = CausalEffect(
            treatment="account_compromised",
            outcome="is_fraud",
            ate=0.8,
            confidence_interval=(0.6, 1.0),
            p_value=0.01,
            is_causal=True,
        )
        assert effect.ate == 0.8
        assert effect.is_causal is True
        assert effect.p_value < 0.05

    def test_non_causal_effect(self):
        effect = CausalEffect(
            treatment="is_new_device",
            outcome="is_fraud",
            ate=0.1,
            is_causal=False,
        )
        assert effect.is_causal is False
        assert effect.ate < 0.2


class TestCausalRiskEngine:
    def setup_method(self):
        self.engine = CausalRiskEngine()

    def test_engine_has_dag(self):
        assert self.engine.dag is not None
        assert self.engine.dag.edge_count > 0

    def test_direct_cause_gets_high_weight(self):
        weights = self.engine.get_causal_feature_weights({
            "account_compromised": 1.0,
        })
        assert weights.weights["account_compromised"] == 1.0

    def test_confounded_feature_gets_low_weight(self):
        weights = self.engine.get_causal_feature_weights({
            "is_new_device": 1.0,
        })
        assert weights.weights["is_new_device"] < 0.5

    def test_unknown_feature_gets_default_weight(self):
        weights = self.engine.get_causal_feature_weights({
            "completely_unknown_feature": 1.0,
        })
        assert weights.weights["completely_unknown_feature"] == 0.7

    def test_mixed_features(self):
        weights = self.engine.get_causal_feature_weights({
            "account_compromised": 1.0,
            "is_new_device": 1.0,
            "amount_zscore": 0.5,
        })
        assert weights.weights["account_compromised"] > weights.weights["is_new_device"]
        assert weights.dag_based is True

    def test_estimate_direct_cause(self):
        effect = self.engine.estimate_treatment_effect("account_compromised", "is_fraud")
        assert effect.is_causal is True
        assert effect.ate > 0.5
        assert effect.p_value < 0.1

    def test_estimate_confounded_feature(self):
        effect = self.engine.estimate_treatment_effect("is_new_device", "is_fraud")
        assert effect.is_causal is False
        assert effect.ate < 0.3

    def test_estimate_no_connection(self):
        effect = self.engine.estimate_treatment_effect("seasonal_effects", "is_fraud")
        assert effect.ate == 0.0
        assert effect.is_causal is False

    def test_effect_caching(self):
        effect1 = self.engine.estimate_treatment_effect("account_compromised")
        effect2 = self.engine.estimate_treatment_effect("account_compromised")
        assert effect1 is effect2

    def test_clear_cache(self):
        self.engine.estimate_treatment_effect("account_compromised")
        self.engine.clear_cache()
        assert len(self.engine._cached_effects) == 0

    def test_custom_dag(self):
        dag = FinancialCausalDAG()
        dag.propose_edge("custom_signal", "is_fraud", "custom mechanism")
        engine = CausalRiskEngine(dag=dag)
        weights = engine.get_causal_feature_weights({"custom_signal": 1.0})
        assert weights.weights["custom_signal"] == 1.0


class TestCausalWeights:
    def test_create_weights(self):
        cw = CausalWeights(
            weights={"feature_a": 0.9, "feature_b": 0.3},
            dag_based=True,
        )
        assert cw.weights["feature_a"] == 0.9
        assert cw.dag_based is True
        assert cw.dowhy_estimated is False
