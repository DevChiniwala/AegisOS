"""
Tests for Temporal.io durable investigation workflows.

Tests workflow data models, fallback activities, and workflow structure.
The workflow/activity logic is tested without requiring the Temporal SDK
(which is an optional dependency).
"""

import sys
import types
from unittest.mock import MagicMock

temporalio_mod = types.ModuleType("temporalio")
temporalio_workflow_mod = types.ModuleType("temporalio.workflow")
temporalio_activity_mod = types.ModuleType("temporalio.activity")
temporalio_common_mod = types.ModuleType("temporalio.common")
temporalio_client_mod = types.ModuleType("temporalio.client")
temporalio_worker_mod = types.ModuleType("temporalio.worker")

_ctx_mgr = MagicMock()
_ctx_mgr.__enter__ = MagicMock(return_value=None)
_ctx_mgr.__exit__ = MagicMock(return_value=False)

_unsafe = types.SimpleNamespace(imports_passed_through=lambda: _ctx_mgr)
temporalio_workflow_mod.unsafe = _unsafe
temporalio_workflow_mod.defn = lambda cls=None, **kwargs: cls if cls else (lambda c: c)
temporalio_workflow_mod.run = lambda fn: fn
temporalio_workflow_mod.signal = lambda fn=None, **kwargs: fn if fn else (lambda f: f)
temporalio_workflow_mod.query = lambda fn=None, **kwargs: fn if fn else (lambda f: f)
temporalio_workflow_mod.execute_activity = MagicMock()
temporalio_workflow_mod.wait_condition = MagicMock()

temporalio_activity_mod.defn = lambda fn=None, **kwargs: fn if fn else (lambda f: f)
temporalio_activity_mod.heartbeat = lambda *args, **kwargs: None

temporalio_common_mod.RetryPolicy = lambda **kwargs: kwargs

sys.modules["temporalio"] = temporalio_mod
sys.modules["temporalio.workflow"] = temporalio_workflow_mod
sys.modules["temporalio.activity"] = temporalio_activity_mod
sys.modules["temporalio.common"] = temporalio_common_mod
sys.modules["temporalio.client"] = temporalio_client_mod
sys.modules["temporalio.worker"] = temporalio_worker_mod

from services.temporal.activities import (
    _fallback_decision,
    _fallback_deep,
    _fallback_triage,
)
from services.temporal.workflows import (
    TASK_QUEUE,
    InvestigationInput,
    InvestigationResult,
    InvestigationWorkflow,
)


class TestInvestigationInput:
    def test_create_input(self):
        inp = InvestigationInput(
            case_id="CASE-TEST001",
            transaction={"amount": 15000, "sender_id": "user_123", "currency": "USD"},
            risk_score=0.87,
            features={"is_new_device": 1.0, "amount_zscore": 3.2},
        )
        assert inp.case_id == "CASE-TEST001"
        assert inp.risk_score == 0.87
        assert inp.features["is_new_device"] == 1.0
        assert inp.investigation_plan == []

    def test_create_input_with_plan(self):
        inp = InvestigationInput(
            case_id="CASE-TEST002",
            transaction={"amount": 500},
            risk_score=0.3,
            features={},
            investigation_plan=["basic_verification"],
        )
        assert inp.investigation_plan == ["basic_verification"]


class TestInvestigationResult:
    def test_create_result(self):
        result = InvestigationResult(
            case_id="CASE-TEST001",
            verdict="BLOCK",
            confidence=0.95,
            findings=["Finding 1", "Finding 2"],
            narrative="Test narrative",
            should_file_sar=True,
            recommendations=["Block transaction"],
        )
        assert result.verdict == "BLOCK"
        assert result.confidence == 0.95
        assert result.should_file_sar is True
        assert len(result.findings) == 2
        assert result.root_causes == []
        assert result.evidence_count == 0

    def test_result_with_all_fields(self):
        result = InvestigationResult(
            case_id="CASE-TEST002",
            verdict="ESCALATE",
            confidence=0.85,
            findings=["f1"],
            narrative="narrative",
            should_file_sar=False,
            recommendations=["review"],
            root_causes=["account_takeover"],
            evidence_count=5,
            agent_count=12,
        )
        assert result.root_causes == ["account_takeover"]
        assert result.evidence_count == 5
        assert result.agent_count == 12


class TestFallbackTriage:
    def test_high_risk(self):
        result = _fallback_triage(
            transaction={"amount": 50000, "sender_id": "user_1"},
            risk_score=0.9,
            features={"is_new_device": 1.0},
        )
        assert "HIGH RISK" in result["findings"][0]
        assert result["agent_count"] == 1
        assert len(result["agent_outputs"]) == 1

    def test_moderate_risk(self):
        result = _fallback_triage(
            transaction={"amount": 5000},
            risk_score=0.6,
            features={},
        )
        assert "MODERATE RISK" in result["findings"][0]

    def test_low_risk(self):
        result = _fallback_triage(
            transaction={"amount": 100},
            risk_score=0.2,
            features={},
        )
        assert "LOW RISK" in result["findings"][0]


class TestFallbackDeep:
    def test_with_device_anomaly(self):
        triage = {"findings": ["Triage: HIGH RISK"], "evidence": [], "agent_outputs": []}
        result = _fallback_deep(
            transaction={"amount": 15000},
            risk_score=0.85,
            features={"is_new_device": 1.0, "transaction_velocity_1h": 8},
            triage_result=triage,
        )
        assert any("Account takeover" in c for c in result["root_causes"])
        assert any("Automated" in c for c in result["root_causes"])
        assert "risk_score=0.850" in result["findings"][-1]

    def test_without_anomalies(self):
        triage = {"findings": ["Triage: LOW RISK"], "evidence": [], "agent_outputs": []}
        result = _fallback_deep(
            transaction={"amount": 100},
            risk_score=0.3,
            features={},
            triage_result=triage,
        )
        assert result["root_causes"] == []
        assert len(result["findings"]) > 0


class TestFallbackDecision:
    def test_block_verdict(self):
        result = _fallback_decision(
            transaction={"amount": 100000, "sender_id": "bad_actor"},
            risk_score=0.95,
            investigation_result={"findings": [], "evidence": []},
        )
        assert result["verdict"] == "BLOCK"
        assert result["confidence"] == 0.95
        assert result["should_file_sar"] is True
        assert "File SAR" in result["recommendations"]

    def test_escalate_verdict(self):
        result = _fallback_decision(
            transaction={"amount": 25000, "sender_id": "user_x"},
            risk_score=0.75,
            investigation_result={"findings": [], "evidence": []},
        )
        assert result["verdict"] == "ESCALATE"
        assert result["confidence"] == 0.85
        assert result["should_file_sar"] is False

    def test_review_verdict(self):
        result = _fallback_decision(
            transaction={"amount": 5000, "sender_id": "user_y"},
            risk_score=0.5,
            investigation_result={"findings": [], "evidence": []},
        )
        assert result["verdict"] == "REVIEW"
        assert result["confidence"] == 0.7

    def test_approve_verdict(self):
        result = _fallback_decision(
            transaction={"amount": 50, "sender_id": "user_z"},
            risk_score=0.2,
            investigation_result={"findings": [], "evidence": []},
        )
        assert result["verdict"] == "APPROVE"
        assert result["confidence"] == 0.9
        assert result["should_file_sar"] is False

    def test_narrative_generated(self):
        result = _fallback_decision(
            transaction={"amount": 15000, "sender_id": "sender_abc"},
            risk_score=0.95,
            investigation_result={"findings": [], "evidence": []},
        )
        assert "sender_abc" in result["narrative"]
        assert "15000" in result["narrative"]
        assert "BLOCK" in result["narrative"]


class TestWorkflowConstants:
    def test_task_queue(self):
        assert TASK_QUEUE == "aegis-investigations"


class TestWorkflowDefinition:
    def test_workflow_class_exists(self):
        assert InvestigationWorkflow is not None

    def test_workflow_has_run_method(self):
        assert hasattr(InvestigationWorkflow, "run")

    def test_workflow_has_signals(self):
        wf = InvestigationWorkflow()
        assert hasattr(wf, "analyst_approve")
        assert hasattr(wf, "analyst_reject")
        assert hasattr(wf, "analyst_escalate")
        assert hasattr(wf, "add_evidence")

    def test_workflow_has_query(self):
        wf = InvestigationWorkflow()
        assert hasattr(wf, "get_status")

    def test_workflow_initial_state(self):
        wf = InvestigationWorkflow()
        status = wf.get_status()
        assert status["phase"] == "initializing"
        assert status["human_decision"] is None
        assert status["analyst_notes"] == []
        assert status["additional_evidence_count"] == 0
