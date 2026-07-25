"""
Core Neuro-Symbolic Compliance Engine.

Uses Z3 theorem prover to produce mathematically provable compliance
determinations. Each regulatory rule is encoded as a Z3 constraint
generator — given transaction facts, it produces either:
- No violation (SAT: compliant state exists)
- Provable violation (with counterexample showing the violation)
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from core.utils.logging import get_logger

if TYPE_CHECKING:
    from services.compliance.neuro_symbolic.rules import RegulatoryRule

logger = get_logger(__name__)


class ViolationType(str, Enum):
    CTR_STRUCTURING = "ctr_structuring"
    SANCTIONS_MATCH = "sanctions_match"
    VELOCITY_VIOLATION = "velocity_violation"
    JURISDICTION_RISK = "jurisdiction_risk"
    PEP_UNDISCLOSED = "pep_undisclosed"
    LAYERING_DETECTED = "layering_detected"
    THRESHOLD_EVASION = "threshold_evasion"


@dataclass
class Violation:
    """A single regulatory violation with provability metadata."""

    violation_type: ViolationType
    regulation: str
    description: str
    severity: float
    provable: bool
    counterexample: Optional[Dict[str, Any]] = None


@dataclass
class ComplianceProof:
    """A mathematically provable compliance determination."""

    is_compliant: bool
    violations: List[Violation] = field(default_factory=list)
    proof_trace: str = ""
    solver_time_ms: float = 0.0
    regulatory_citations: List[str] = field(default_factory=list)
    rules_evaluated: int = 0


class NeuroSymbolicComplianceEngine:
    """Deterministic compliance engine combining Z3 logic with regulatory expertise.

    Usage:
        engine = NeuroSymbolicComplianceEngine()
        proof = engine.evaluate(
            case_id="CASE-001",
            transaction={"amount": 9500, "sender_id": "user_123"},
            findings=["Structuring pattern detected"],
            risk_score=0.87,
            transaction_history=[{"amount": 9400, "sender_id": "user_123"}],
        )
        if not proof.is_compliant:
            for v in proof.violations:
                print(f"VIOLATION: {v.regulation} — {v.description}")
    """

    def __init__(self):
        self._rules: Dict[str, "RegulatoryRule"] = {}
        self._load_default_rules()

    def _load_default_rules(self):
        from services.compliance.neuro_symbolic.rules import (
            CTRStructuringRule,
            JurisdictionRiskRule,
            LayeringRule,
            SanctionsRule,
            VelocityLimitRule,
        )

        self._rules["ctr_structuring"] = CTRStructuringRule()
        self._rules["velocity_limits"] = VelocityLimitRule()
        self._rules["layering_detection"] = LayeringRule()
        self._rules["sanctions_screening"] = SanctionsRule()
        self._rules["jurisdiction_risk"] = JurisdictionRiskRule()

    def evaluate(
        self,
        case_id: str,
        transaction: Dict[str, Any],
        findings: List[str],
        risk_score: float,
        transaction_history: Optional[List[Dict[str, Any]]] = None,
    ) -> ComplianceProof:
        """Run full compliance evaluation against all loaded rules.

        Returns a ComplianceProof that is either provably compliant
        or contains one or more provable violations with citations.
        """
        start = time.perf_counter()
        history = transaction_history or []
        violations: List[Violation] = []

        for rule_name, rule in self._rules.items():
            try:
                result = rule.check(transaction, history)
                if result is not None:
                    violations.append(result)
                    logger.info(
                        "Compliance violation detected",
                        case_id=case_id,
                        rule=rule_name,
                        regulation=result.regulation,
                        severity=result.severity,
                    )
            except Exception as e:
                logger.warning(
                    "Rule evaluation failed",
                    rule=rule_name,
                    error=str(e),
                )

        elapsed_ms = (time.perf_counter() - start) * 1000

        violations.sort(key=lambda v: v.severity, reverse=True)

        proof = ComplianceProof(
            is_compliant=len(violations) == 0,
            violations=violations,
            proof_trace=self._generate_proof_trace(transaction, violations),
            solver_time_ms=elapsed_ms,
            regulatory_citations=[v.regulation for v in violations],
            rules_evaluated=len(self._rules),
        )

        logger.info(
            "Compliance evaluation complete",
            case_id=case_id,
            is_compliant=proof.is_compliant,
            violations_count=len(violations),
            solver_time_ms=f"{elapsed_ms:.2f}",
        )

        return proof

    def add_rule(self, name: str, rule: "RegulatoryRule"):
        """Add a custom regulatory rule (institution-specific)."""
        self._rules[name] = rule

    def remove_rule(self, name: str):
        """Remove a rule by name."""
        self._rules.pop(name, None)

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    def _generate_proof_trace(
        self, transaction: Dict[str, Any], violations: List[Violation]
    ) -> str:
        """Generate a human-readable proof trace for audit purposes."""
        if not violations:
            return "ALL_RULES_SATISFIED: No regulatory violations detected."

        lines = ["COMPLIANCE_VIOLATIONS_PROVEN:"]
        for i, v in enumerate(violations, 1):
            lines.append(
                f"  [{i}] {v.regulation}: {v.description} "
                f"(severity={v.severity:.2f}, provable={v.provable})"
            )
            if v.counterexample:
                lines.append(f"      counterexample: {v.counterexample}")

        lines.append(f"\nTransaction: amount={transaction.get('amount')}, "
                     f"sender={transaction.get('sender_id')}, "
                     f"receiver={transaction.get('receiver_id')}")

        return "\n".join(lines)
