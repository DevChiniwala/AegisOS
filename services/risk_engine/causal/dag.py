"""
Financial Causal Directed Acyclic Graph (DAG).

Encodes domain-expert knowledge about causal relationships
between features and fraud outcomes. Used by DoWhy for
identification and estimation of causal effects.

Design: Hybrid approach
- Base edges are hardcoded (domain expert knowledge, peer-reviewed research)
- LLM augmentation proposes new edges validated by domain constraints
"""

from dataclasses import dataclass
from typing import List, Set, Tuple

from core.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CausalEdge:
    """A directed causal edge in the financial fraud DAG."""

    source: str
    target: str
    mechanism: str = ""
    strength: float = 1.0
    validated: bool = True


class FinancialCausalDAG:
    """Domain-expert causal graph for financial fraud detection.

    Encodes which features CAUSE fraud vs merely correlate with it.
    Used by DoWhy for causal identification and effect estimation.

    Key insight: "is_new_device" doesn't cause fraud — "account_compromised"
    causes BOTH new device usage AND fraud. Without the DAG, the model
    over-weights "is_new_device" and generates false positives.
    """

    def __init__(self):
        self._edges: List[CausalEdge] = []
        self._nodes: Set[str] = set()
        self._load_base_dag()

    def _load_base_dag(self):
        """Load the base financial causal DAG from domain expertise."""
        base_edges = [
            # Direct causes of fraud
            ("account_compromised", "is_fraud", "credential theft enables unauthorized transactions"),
            ("insider_threat", "is_fraud", "malicious insider bypasses controls"),
            ("synthetic_identity", "is_fraud", "fabricated identity enables account opening fraud"),
            ("structuring_intent", "is_fraud", "deliberate structuring to evade CTR"),

            # Account compromise causes observable signals
            ("account_compromised", "is_new_device", "attacker uses different device"),
            ("account_compromised", "geo_velocity_anomaly", "attacker in different location"),
            ("account_compromised", "is_new_ip", "attacker on different network"),
            ("account_compromised", "session_anomaly", "stolen session or new login"),

            # Structuring intent causes observable patterns
            ("structuring_intent", "amount_near_threshold", "transactions kept below $10K"),
            ("structuring_intent", "high_transaction_velocity", "multiple sub-threshold transactions"),
            ("structuring_intent", "round_amounts", "rounded amounts for cash structuring"),

            # Layering intent causes graph patterns
            ("layering_intent", "rapid_relay_chain", "funds move through intermediaries quickly"),
            ("layering_intent", "new_recipient_burst", "many new recipients in short time"),
            ("layering_intent", "is_fraud", "layering is a form of money laundering"),

            # Legitimate causes of signals (confounders)
            ("legitimate_travel", "geo_velocity_anomaly", "real travel triggers geo alerts"),
            ("new_phone", "is_new_device", "customer upgraded device legitimately"),
            ("business_activity", "high_transaction_velocity", "legitimate business volume"),
            ("salary_payment", "round_amounts", "payroll uses round numbers"),

            # Environment confounders
            ("time_of_day", "transaction_velocity_1h", "batch processing at certain hours"),
            ("day_of_week", "amount_zscore", "payday patterns"),
            ("seasonal_effects", "amount_to_max_ratio", "holiday spending spikes"),
        ]

        for source, target, mechanism in base_edges:
            self._edges.append(CausalEdge(source=source, target=target, mechanism=mechanism))
            self._nodes.add(source)
            self._nodes.add(target)

    @property
    def edges(self) -> List[Tuple[str, str]]:
        """Return edge list as (source, target) tuples."""
        return [(e.source, e.target) for e in self._edges]

    @property
    def nodes(self) -> Set[str]:
        return self._nodes.copy()

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def get_causes_of(self, target: str) -> List[str]:
        """Get all direct causes of a given node."""
        return [e.source for e in self._edges if e.target == target]

    def get_effects_of(self, source: str) -> List[str]:
        """Get all direct effects of a given node."""
        return [e.target for e in self._edges if e.source == source]

    def get_confounders(self, treatment: str, outcome: str) -> List[str]:
        """Find common causes of both treatment and outcome (confounders)."""
        treatment_causes = set(self.get_causes_of(treatment))
        outcome_causes = set(self.get_causes_of(outcome))
        return list(treatment_causes & outcome_causes)

    def is_causal_path(self, source: str, target: str) -> bool:
        """Check if there's a directed path from source to target."""
        visited = set()
        queue = [source]
        while queue:
            current = queue.pop(0)
            if current == target:
                return True
            if current in visited:
                continue
            visited.add(current)
            queue.extend(self.get_effects_of(current))
        return False

    def propose_edge(
        self,
        source: str,
        target: str,
        mechanism: str = "",
    ) -> bool:
        """Validate a proposed edge against domain constraints.

        Constraints:
        1. No cycles (would violate DAG property)
        2. Observable signals cannot cause latent states
        3. "is_fraud" cannot cause other features (effect, not cause)
        """
        LATENT_STATES = {"account_compromised", "insider_threat", "synthetic_identity",
                         "structuring_intent", "layering_intent"}
        OBSERVABLE_SIGNALS = {"is_new_device", "geo_velocity_anomaly", "is_new_ip",
                             "amount_near_threshold", "high_transaction_velocity",
                             "round_amounts", "rapid_relay_chain"}

        if source == target:
            return False

        if self.is_causal_path(target, source):
            logger.warning("Rejected edge: would create cycle", source=source, target=target)
            return False

        if source in OBSERVABLE_SIGNALS and target in LATENT_STATES:
            logger.warning("Rejected edge: observable cannot cause latent", source=source, target=target)
            return False

        if source == "is_fraud":
            logger.warning("Rejected edge: fraud outcome cannot be a cause", source=source, target=target)
            return False

        self._edges.append(CausalEdge(
            source=source, target=target, mechanism=mechanism, validated=False
        ))
        self._nodes.add(source)
        self._nodes.add(target)
        logger.info("Edge proposed and accepted", source=source, target=target)
        return True

    def to_gml(self) -> str:
        """Export DAG in GML format for DoWhy."""
        lines = ["graph [directed 1"]
        for node in sorted(self._nodes):
            lines.append(f'  node [id "{node}" label "{node}"]')
        for edge in self._edges:
            lines.append(f'  edge [source "{edge.source}" target "{edge.target}"]')
        lines.append("]")
        return "\n".join(lines)

    def to_dot(self) -> str:
        """Export DAG in DOT format for visualization."""
        lines = ["digraph FinancialFraudDAG {"]
        lines.append("  rankdir=LR;")
        for edge in self._edges:
            lines.append(f'  "{edge.source}" -> "{edge.target}";')
        lines.append("}")
        return "\n".join(lines)
