"""
Tests for the Neuro-Symbolic Compliance Engine.

Tests rule evaluation, violation detection, and proof generation
without requiring Z3 (falls back to deterministic logic).
"""

import pytest
from services.compliance.neuro_symbolic.engine import (
    NeuroSymbolicComplianceEngine,
    ComplianceProof,
    Violation,
    ViolationType,
)
from services.compliance.neuro_symbolic.rules import (
    CTRStructuringRule,
    VelocityLimitRule,
    LayeringRule,
    SanctionsRule,
    JurisdictionRiskRule,
    RegulatoryRule,
)


class TestComplianceProof:
    def test_compliant_proof(self):
        proof = ComplianceProof(is_compliant=True)
        assert proof.is_compliant is True
        assert proof.violations == []
        assert proof.rules_evaluated == 0

    def test_non_compliant_proof(self):
        v = Violation(
            violation_type=ViolationType.CTR_STRUCTURING,
            regulation="31 CFR 1010.311",
            description="Structuring detected",
            severity=0.9,
            provable=True,
        )
        proof = ComplianceProof(
            is_compliant=False,
            violations=[v],
            regulatory_citations=["31 CFR 1010.311"],
            rules_evaluated=5,
        )
        assert proof.is_compliant is False
        assert len(proof.violations) == 1
        assert proof.regulatory_citations == ["31 CFR 1010.311"]


class TestViolation:
    def test_create_violation(self):
        v = Violation(
            violation_type=ViolationType.SANCTIONS_MATCH,
            regulation="31 CFR Part 501",
            description="Sanctioned jurisdiction",
            severity=1.0,
            provable=True,
            counterexample={"jurisdiction": "IR"},
        )
        assert v.violation_type == ViolationType.SANCTIONS_MATCH
        assert v.severity == 1.0
        assert v.counterexample == {"jurisdiction": "IR"}


class TestCTRStructuringRule:
    def setup_method(self):
        self.rule = CTRStructuringRule()

    def test_regulation_id(self):
        assert "31 CFR 1010.311" in self.rule.regulation_id

    def test_no_violation_single_transaction(self):
        result = self.rule.check(
            transaction={"amount": 5000, "sender_id": "user_1"},
            history=[],
        )
        assert result is None

    def test_no_violation_below_threshold(self):
        result = self.rule.check(
            transaction={"amount": 3000, "sender_id": "user_1"},
            history=[{"amount": 2000, "sender_id": "user_1"}],
        )
        assert result is None

    def test_structuring_detected(self):
        result = self.rule.check(
            transaction={"amount": 9500, "sender_id": "user_1"},
            history=[
                {"amount": 9400, "sender_id": "user_1"},
            ],
        )
        assert result is not None
        assert result.violation_type == ViolationType.CTR_STRUCTURING
        assert result.severity == 0.9
        assert "user_1" in result.description
        assert result.counterexample["total"] == 18900.0

    def test_structuring_three_transactions(self):
        result = self.rule.check(
            transaction={"amount": 4000, "sender_id": "user_2"},
            history=[
                {"amount": 3500, "sender_id": "user_2"},
                {"amount": 3500, "sender_id": "user_2"},
            ],
        )
        assert result is not None
        assert result.counterexample["count"] == 3

    def test_no_structuring_different_senders(self):
        result = self.rule.check(
            transaction={"amount": 9500, "sender_id": "user_1"},
            history=[
                {"amount": 9400, "sender_id": "user_2"},  # different sender
            ],
        )
        assert result is None

    def test_no_structuring_above_threshold(self):
        result = self.rule.check(
            transaction={"amount": 15000, "sender_id": "user_1"},
            history=[
                {"amount": 9000, "sender_id": "user_1"},
            ],
        )
        assert result is None


class TestVelocityLimitRule:
    def setup_method(self):
        self.rule = VelocityLimitRule()

    def test_regulation_id(self):
        assert "FATF" in self.rule.regulation_id

    def test_no_violation_low_velocity(self):
        result = self.rule.check(
            transaction={"amount": 1000, "sender_id": "user_1"},
            history=[{"sender_id": "user_1"}] * 5,
        )
        assert result is None

    def test_velocity_violation(self):
        result = self.rule.check(
            transaction={"amount": 1000, "sender_id": "user_1"},
            history=[{"sender_id": "user_1"}] * 12,
        )
        assert result is not None
        assert result.violation_type == ViolationType.VELOCITY_VIOLATION
        assert result.severity == 0.7
        assert "13" in result.description

    def test_velocity_exact_threshold(self):
        result = self.rule.check(
            transaction={"amount": 1000, "sender_id": "user_1"},
            history=[{"sender_id": "user_1"}] * 9,
        )
        assert result is None


class TestLayeringRule:
    def setup_method(self):
        self.rule = LayeringRule()

    def test_regulation_id(self):
        assert "FinCEN" in self.rule.regulation_id

    def test_no_layering_short_chain(self):
        result = self.rule.check(
            transaction={"sender_id": "A", "receiver_id": "B"},
            history=[
                {"sender_id": "B", "receiver_id": "C", "timestamp": "2024-01-01T00:01:00"},
            ],
        )
        assert result is None

    def test_layering_detected(self):
        result = self.rule.check(
            transaction={"sender_id": "A", "receiver_id": "B"},
            history=[
                {"sender_id": "B", "receiver_id": "C", "timestamp": "2024-01-01T00:03:00"},
                {"sender_id": "C", "receiver_id": "D", "timestamp": "2024-01-01T00:02:00"},
                {"sender_id": "D", "receiver_id": "E", "timestamp": "2024-01-01T00:01:00"},
            ],
        )
        assert result is not None
        assert result.violation_type == ViolationType.LAYERING_DETECTED
        assert result.severity == 0.85
        assert "4-hop" in result.description

    def test_no_receiver_no_layering(self):
        result = self.rule.check(
            transaction={"sender_id": "A"},
            history=[],
        )
        assert result is None


class TestSanctionsRule:
    def setup_method(self):
        self.rule = SanctionsRule()

    def test_regulation_id(self):
        assert "OFAC" in self.rule.regulation_id

    def test_no_sanctions_match(self):
        result = self.rule.check(
            transaction={"receiver_jurisdiction": "US", "sender_jurisdiction": "GB"},
            history=[],
        )
        assert result is None

    def test_sanctions_match_receiver(self):
        result = self.rule.check(
            transaction={"receiver_jurisdiction": "IR", "sender_jurisdiction": "US"},
            history=[],
        )
        assert result is not None
        assert result.violation_type == ViolationType.SANCTIONS_MATCH
        assert result.severity == 1.0
        assert "IR" in result.description

    def test_sanctions_match_sender(self):
        result = self.rule.check(
            transaction={"receiver_jurisdiction": "US", "sender_jurisdiction": "KP"},
            history=[],
        )
        assert result is not None
        assert result.counterexample == {"jurisdiction": "KP"}

    def test_sanctions_north_korea(self):
        result = self.rule.check(
            transaction={"receiver_jurisdiction": "KP"},
            history=[],
        )
        assert result is not None
        assert result.severity == 1.0


class TestJurisdictionRiskRule:
    def setup_method(self):
        self.rule = JurisdictionRiskRule()

    def test_no_risk_clean_jurisdiction(self):
        result = self.rule.check(
            transaction={"receiver_jurisdiction": "US", "sender_jurisdiction": "GB"},
            history=[],
        )
        assert result is None

    def test_fatf_high_risk_detected(self):
        result = self.rule.check(
            transaction={"receiver_jurisdiction": "MM"},
            history=[],
        )
        assert result is not None
        assert result.violation_type == ViolationType.JURISDICTION_RISK
        assert result.severity == 0.6
        assert "MM" in result.description

    def test_fatf_sender_jurisdiction(self):
        result = self.rule.check(
            transaction={"receiver_jurisdiction": "US", "sender_jurisdiction": "YE"},
            history=[],
        )
        assert result is not None
        assert result.counterexample == {"jurisdiction": "YE"}


class TestNeuroSymbolicEngine:
    def setup_method(self):
        self.engine = NeuroSymbolicComplianceEngine()

    def test_engine_loads_default_rules(self):
        assert self.engine.rule_count == 5

    def test_compliant_transaction(self):
        proof = self.engine.evaluate(
            case_id="CASE-001",
            transaction={"amount": 500, "sender_id": "user_1", "receiver_jurisdiction": "US"},
            findings=[],
            risk_score=0.2,
        )
        assert proof.is_compliant is True
        assert proof.violations == []
        assert proof.rules_evaluated == 5
        assert proof.solver_time_ms > 0

    def test_structuring_violation(self):
        proof = self.engine.evaluate(
            case_id="CASE-002",
            transaction={"amount": 9500, "sender_id": "user_1"},
            findings=["Possible structuring"],
            risk_score=0.85,
            transaction_history=[
                {"amount": 9400, "sender_id": "user_1"},
            ],
        )
        assert proof.is_compliant is False
        assert any(v.violation_type == ViolationType.CTR_STRUCTURING for v in proof.violations)
        assert any("31 CFR 1010.311" in c for c in proof.regulatory_citations)

    def test_sanctions_violation(self):
        proof = self.engine.evaluate(
            case_id="CASE-003",
            transaction={"amount": 50000, "sender_id": "user_x", "receiver_jurisdiction": "IR"},
            findings=[],
            risk_score=0.95,
        )
        assert proof.is_compliant is False
        assert any(v.violation_type == ViolationType.SANCTIONS_MATCH for v in proof.violations)
        assert any(v.severity == 1.0 for v in proof.violations)

    def test_multiple_violations(self):
        proof = self.engine.evaluate(
            case_id="CASE-004",
            transaction={
                "amount": 9800,
                "sender_id": "user_rapid",
                "receiver_jurisdiction": "MM",
            },
            findings=[],
            risk_score=0.9,
            transaction_history=[
                {"amount": 9700, "sender_id": "user_rapid"},
            ] + [{"sender_id": "user_rapid"}] * 15,
        )
        assert proof.is_compliant is False
        assert len(proof.violations) >= 2
        assert proof.violations[0].severity >= proof.violations[1].severity

    def test_proof_trace_compliant(self):
        proof = self.engine.evaluate(
            case_id="CASE-005",
            transaction={"amount": 100, "sender_id": "user_clean"},
            findings=[],
            risk_score=0.1,
        )
        assert "ALL_RULES_SATISFIED" in proof.proof_trace

    def test_proof_trace_violation(self):
        proof = self.engine.evaluate(
            case_id="CASE-006",
            transaction={"amount": 5000, "sender_id": "user_x", "receiver_jurisdiction": "SY"},
            findings=[],
            risk_score=0.9,
        )
        assert "COMPLIANCE_VIOLATIONS_PROVEN" in proof.proof_trace
        assert "31 CFR Part 501" in proof.proof_trace

    def test_add_custom_rule(self):
        class CustomRule(RegulatoryRule):
            @property
            def regulation_id(self):
                return "CUSTOM-001"

            @property
            def description(self):
                return "Custom test rule"

            def check(self, transaction, history):
                if transaction.get("custom_flag"):
                    return Violation(
                        violation_type=ViolationType.THRESHOLD_EVASION,
                        regulation="CUSTOM-001",
                        description="Custom violation",
                        severity=0.5,
                        provable=False,
                    )
                return None

        self.engine.add_rule("custom", CustomRule())
        assert self.engine.rule_count == 6

        proof = self.engine.evaluate(
            case_id="CASE-007",
            transaction={"amount": 100, "custom_flag": True},
            findings=[],
            risk_score=0.5,
        )
        assert not proof.is_compliant
        assert any(v.regulation == "CUSTOM-001" for v in proof.violations)

    def test_remove_rule(self):
        self.engine.remove_rule("sanctions_screening")
        assert self.engine.rule_count == 4

        proof = self.engine.evaluate(
            case_id="CASE-008",
            transaction={"amount": 5000, "receiver_jurisdiction": "IR"},
            findings=[],
            risk_score=0.9,
        )
        assert not any(v.violation_type == ViolationType.SANCTIONS_MATCH for v in proof.violations)
