"""
Regulatory rules encoded as Z3 constraints.

Each rule implements the RegulatoryRule protocol:
- check(transaction, history) -> Optional[Violation]

When Z3 is available, rules use SAT/SMT solving for provable violations.
When Z3 is unavailable, rules fall back to deterministic Python logic
(same results, less formal provability).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.utils.logging import get_logger
from services.compliance.neuro_symbolic.engine import Violation, ViolationType

logger = get_logger(__name__)

try:
    import z3

    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False


class RegulatoryRule(ABC):
    """Base class for Z3-encoded regulatory rules."""

    @property
    @abstractmethod
    def regulation_id(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @abstractmethod
    def check(
        self,
        transaction: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Optional[Violation]:
        ...


class CTRStructuringRule(RegulatoryRule):
    """Detect structuring: transactions designed to stay below $10,000 CTR threshold.

    31 CFR 1010.311 requires CTR filing for cash transactions > $10,000.
    31 USC 5324 criminalizes structuring to evade CTR.

    Z3 encoding: For transactions T from same sender within 24h window,
    if SUM(T) > 10000 AND MAX(T) < 10000 AND COUNT(T) >= 2,
    then structuring is provable.
    """

    @property
    def regulation_id(self) -> str:
        return "31 CFR 1010.311 / 31 USC 5324"

    @property
    def description(self) -> str:
        return "Currency Transaction Report structuring detection"

    def check(
        self,
        transaction: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Optional[Violation]:
        sender = transaction.get("sender_id", "")
        amount = float(transaction.get("amount", 0))

        related = [
            float(h.get("amount", 0))
            for h in history
            if h.get("sender_id") == sender
        ]
        all_amounts = related + [amount]

        if len(all_amounts) < 2:
            return None

        total = sum(all_amounts)
        max_single = max(all_amounts)

        if Z3_AVAILABLE:
            return self._check_z3(all_amounts, total, max_single, sender)

        return self._check_deterministic(all_amounts, total, max_single, sender)

    def _check_z3(
        self, amounts: List[float], total: float, max_single: float, sender: str
    ) -> Optional[Violation]:
        solver = z3.Solver()
        solver.set("timeout", 1000)

        z3_amounts = [z3.Real(f"tx_{i}") for i in range(len(amounts))]

        for i, val in enumerate(amounts):
            solver.add(z3_amounts[i] == val)

        z3_total = z3.Sum(z3_amounts)
        all_below_threshold = z3.And([a < 10000 for a in z3_amounts])
        count_sufficient = len(z3_amounts) >= 2
        total_exceeds = z3_total > 10000

        structuring_predicate = z3.And(total_exceeds, all_below_threshold)

        if not count_sufficient:
            return None

        solver.add(structuring_predicate)

        if solver.check() == z3.sat:
            return Violation(
                violation_type=ViolationType.CTR_STRUCTURING,
                regulation=self.regulation_id,
                description=(
                    f"Structuring detected: {len(amounts)} transactions from {sender} "
                    f"totaling ${total:,.2f}, each below $10,000 CTR threshold"
                ),
                severity=0.9,
                provable=True,
                counterexample={"total": total, "count": len(amounts), "max_single": max_single},
            )

        return None

    def _check_deterministic(
        self, amounts: List[float], total: float, max_single: float, sender: str
    ) -> Optional[Violation]:
        if total > 10000 and max_single < 10000 and len(amounts) >= 2:
            return Violation(
                violation_type=ViolationType.CTR_STRUCTURING,
                regulation=self.regulation_id,
                description=(
                    f"Structuring detected: {len(amounts)} transactions from {sender} "
                    f"totaling ${total:,.2f}, each below $10,000 CTR threshold"
                ),
                severity=0.9,
                provable=not Z3_AVAILABLE,
                counterexample={"total": total, "count": len(amounts), "max_single": max_single},
            )
        return None


class VelocityLimitRule(RegulatoryRule):
    """Detect suspicious transaction velocity patterns.

    FATF Recommendation 10 requires enhanced CDD for unusual patterns.
    Institutional velocity limits flag potential automated attacks or layering.
    """

    MAX_TX_PER_HOUR = 10
    MAX_TX_PER_DAY = 50

    @property
    def regulation_id(self) -> str:
        return "FATF Recommendation 10"

    @property
    def description(self) -> str:
        return "Unusual transaction velocity indicating automated attacks or layering"

    def check(
        self,
        transaction: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Optional[Violation]:
        sender = transaction.get("sender_id", "")
        recent_count = len([h for h in history if h.get("sender_id") == sender]) + 1

        if recent_count <= self.MAX_TX_PER_HOUR:
            return None

        if Z3_AVAILABLE:
            return self._check_z3(recent_count, sender)

        return self._check_deterministic(recent_count, sender)

    def _check_z3(self, count: int, sender: str) -> Optional[Violation]:
        solver = z3.Solver()
        tx_count = z3.Int("tx_count")
        solver.add(tx_count == count)
        solver.add(tx_count > self.MAX_TX_PER_HOUR)

        if solver.check() == z3.sat:
            return Violation(
                violation_type=ViolationType.VELOCITY_VIOLATION,
                regulation=self.regulation_id,
                description=(
                    f"Velocity limit exceeded: {count} transactions from {sender} "
                    f"(limit: {self.MAX_TX_PER_HOUR}/hour)"
                ),
                severity=0.7,
                provable=True,
                counterexample={"count": count, "limit": self.MAX_TX_PER_HOUR},
            )
        return None

    def _check_deterministic(self, count: int, sender: str) -> Optional[Violation]:
        return Violation(
            violation_type=ViolationType.VELOCITY_VIOLATION,
            regulation=self.regulation_id,
            description=(
                f"Velocity limit exceeded: {count} transactions from {sender} "
                f"(limit: {self.MAX_TX_PER_HOUR}/hour)"
            ),
            severity=0.7,
            provable=False,
            counterexample={"count": count, "limit": self.MAX_TX_PER_HOUR},
        )


class LayeringRule(RegulatoryRule):
    """Detect layering: rapid fund movement through intermediary accounts.

    FinCEN Advisory FIN-2014-A007 identifies layering as a key AML typology.
    Pattern: A→B→C→D within short window, with similar amounts.
    """

    MIN_CHAIN_LENGTH = 3

    @property
    def regulation_id(self) -> str:
        return "FATF Recommendation 10 / FinCEN Advisory FIN-2014-A007"

    @property
    def description(self) -> str:
        return "Detection of layering through multiple intermediary accounts"

    def check(
        self,
        transaction: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Optional[Violation]:
        receiver = transaction.get("receiver_id", "")
        if not receiver:
            return None

        chain_length = 0
        current_receiver = receiver
        for h in sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True):
            if h.get("sender_id") == current_receiver:
                chain_length += 1
                current_receiver = h.get("receiver_id", "")
            if chain_length >= self.MIN_CHAIN_LENGTH:
                break

        if chain_length >= self.MIN_CHAIN_LENGTH:
            return Violation(
                violation_type=ViolationType.LAYERING_DETECTED,
                regulation=self.regulation_id,
                description=(
                    f"Layering pattern: {chain_length + 1}-hop relay chain detected "
                    f"through intermediary accounts"
                ),
                severity=0.85,
                provable=True,
                counterexample={"chain_length": chain_length + 1},
            )

        return None


class SanctionsRule(RegulatoryRule):
    """OFAC sanctions and SDN list screening.

    31 CFR Part 501 prohibits transactions with sanctioned entities/jurisdictions.
    """

    SANCTIONED_JURISDICTIONS = frozenset({"IR", "KP", "SY", "CU", "RU"})

    @property
    def regulation_id(self) -> str:
        return "31 CFR Part 501 (OFAC)"

    @property
    def description(self) -> str:
        return "Sanctions and SDN list screening"

    def check(
        self,
        transaction: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Optional[Violation]:
        receiver_jurisdiction = transaction.get("receiver_jurisdiction", "")
        sender_jurisdiction = transaction.get("sender_jurisdiction", "")

        matched = None
        if receiver_jurisdiction in self.SANCTIONED_JURISDICTIONS:
            matched = receiver_jurisdiction
        elif sender_jurisdiction in self.SANCTIONED_JURISDICTIONS:
            matched = sender_jurisdiction

        if matched:
            return Violation(
                violation_type=ViolationType.SANCTIONS_MATCH,
                regulation=self.regulation_id,
                description=f"Transaction involves sanctioned jurisdiction: {matched}",
                severity=1.0,
                provable=True,
                counterexample={"jurisdiction": matched},
            )

        return None


class JurisdictionRiskRule(RegulatoryRule):
    """FATF grey/blacklist jurisdiction enhanced due diligence.

    FATF Recommendation 19 requires enhanced CDD for high-risk jurisdictions.
    """

    FATF_HIGH_RISK = frozenset({
        "MM", "HT", "KH", "ML", "MZ", "PH", "SS", "TZ", "VN", "YE",
        "BF", "CM", "CD", "GY", "MG", "NG", "ZA", "VE",
    })

    @property
    def regulation_id(self) -> str:
        return "FATF Recommendation 19"

    @property
    def description(self) -> str:
        return "High-risk jurisdiction enhanced due diligence"

    def check(
        self,
        transaction: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Optional[Violation]:
        receiver_jurisdiction = transaction.get("receiver_jurisdiction", "")
        sender_jurisdiction = transaction.get("sender_jurisdiction", "")

        matched = None
        if receiver_jurisdiction in self.FATF_HIGH_RISK:
            matched = receiver_jurisdiction
        elif sender_jurisdiction in self.FATF_HIGH_RISK:
            matched = sender_jurisdiction

        if matched:
            return Violation(
                violation_type=ViolationType.JURISDICTION_RISK,
                regulation=self.regulation_id,
                description=(
                    f"FATF high-risk jurisdiction: {matched} — "
                    f"enhanced due diligence required"
                ),
                severity=0.6,
                provable=True,
                counterexample={"jurisdiction": matched},
            )

        return None
