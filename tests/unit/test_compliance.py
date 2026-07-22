"""Tests for compliance engine fixes."""
import pytest
from unittest.mock import MagicMock
from services.compliance.engine import ComplianceEngine
from core.schemas.investigation import CaseStatus, CasePriority


class TestComplianceEngine:
    def setup_method(self):
        self.engine = ComplianceEngine()

    def test_should_file_sar_closed_fraud(self):
        case = MagicMock()
        case.priority = CasePriority.HIGH
        case.status = CaseStatus.CLOSED
        case.verdict = "FRAUD"
        assert self.engine.should_file_sar(case) is True

    def test_should_not_file_sar_open_case(self):
        case = MagicMock()
        case.priority = CasePriority.HIGH
        case.status = CaseStatus.OPEN
        case.verdict = "FRAUD"
        assert self.engine.should_file_sar(case) is False

    def test_should_not_file_sar_non_fraud_verdict(self):
        case = MagicMock()
        case.priority = CasePriority.HIGH
        case.status = CaseStatus.CLOSED
        case.verdict = "LEGITIMATE"
        assert self.engine.should_file_sar(case) is False

    def test_should_not_file_sar_low_priority(self):
        case = MagicMock()
        case.priority = CasePriority.LOW
        case.status = CaseStatus.CLOSED
        case.verdict = "FRAUD"
        assert self.engine.should_file_sar(case) is False

    def test_generate_sar_report_uses_case_id(self):
        case = MagicMock()
        case.case_id = "CASE-001"
        case.priority = CasePriority.HIGH
        report = self.engine.generate_sar_report(case)
        assert "CASE-001" in report

    def test_aml_check_high_amount(self):
        tx = MagicMock()
        tx.amount = 15000
        user = MagicMock()
        result = self.engine.check_aml(tx, user)
        assert result.is_compliant is False
        assert "CTR_THRESHOLD_EXCEEDED" in result.flags
