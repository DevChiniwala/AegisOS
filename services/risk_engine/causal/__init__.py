"""
Causal Inference Risk Scoring.

Uses Microsoft DoWhy/EconML to distinguish causal from correlational
features in fraud detection. Eliminates false positives caused by
spurious correlations (e.g., "new device" correlates with fraud
but doesn't cause it — account compromise causes both).

Requires: pip install aegisos[causal]
"""

from services.risk_engine.causal.dag import FinancialCausalDAG
from services.risk_engine.causal.engine import CausalEffect, CausalRiskEngine

__all__ = [
    "CausalRiskEngine",
    "CausalEffect",
    "FinancialCausalDAG",
]
