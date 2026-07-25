"""
Neuro-Symbolic Compliance Engine.

Combines Z3 theorem prover (deterministic, provable regulatory logic)
with LLM-augmented interpretation for ambiguous regulatory language.

Architecture:
1. Encode regulations as Z3 first-order logic constraints
2. Encode transaction facts as Z3 constants
3. Check satisfiability: violations are mathematically proven
4. For subjective language ("unusual", "significant"), LLM interprets
   but Z3 post-validates logical consistency

Requires: pip install aegisos[compliance]
"""

try:
    from services.compliance.neuro_symbolic.engine import (
        NeuroSymbolicComplianceEngine,
        ComplianceProof,
        Violation,
        ViolationType,
    )

    __all__ = [
        "NeuroSymbolicComplianceEngine",
        "ComplianceProof",
        "Violation",
        "ViolationType",
    ]
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    __all__ = ["Z3_AVAILABLE"]
