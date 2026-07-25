"""
Temporal.io Durable Agent Orchestration.

Wraps the LangGraph 12-agent swarm in Temporal Workflows for:
- Crash recovery (state persisted by Temporal server)
- Multi-day pauses for HITL review
- Signal-based analyst intervention
- Timeout escalation
- Independent retry policies per investigation phase

Requires: pip install aegisos[temporal]
"""

try:
    from services.temporal.client import TemporalInvestigationClient
    from services.temporal.workflows import (
        InvestigationInput,
        InvestigationResult,
        InvestigationWorkflow,
    )

    __all__ = [
        "InvestigationWorkflow",
        "InvestigationInput",
        "InvestigationResult",
        "TemporalInvestigationClient",
    ]
    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False
    __all__ = ["TEMPORAL_AVAILABLE"]
