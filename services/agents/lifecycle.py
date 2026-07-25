"""
Investigation Lifecycle State Machine.

Enforces valid state transitions for investigations.
Each transition emits an event to the event store.
"""
from enum import Enum
from typing import Dict, List, Optional, Set

from core.events.event_store import get_event_store
from core.events.models import EventType, InvestigationEvent
from core.utils.logging import get_logger

logger = get_logger(__name__)


class InvestigationPhase(str, Enum):
    ALERT = "alert"
    TRIAGE = "triage"
    INVESTIGATE = "investigate"
    EVIDENCE = "evidence"
    REVIEW = "review"
    DECIDE = "decide"
    REPORT = "report"
    CLOSED = "closed"
    ESCALATED = "escalated"


VALID_TRANSITIONS: Dict[InvestigationPhase, Set[InvestigationPhase]] = {
    InvestigationPhase.ALERT: {InvestigationPhase.TRIAGE, InvestigationPhase.CLOSED},
    InvestigationPhase.TRIAGE: {InvestigationPhase.INVESTIGATE, InvestigationPhase.CLOSED, InvestigationPhase.ESCALATED},
    InvestigationPhase.INVESTIGATE: {InvestigationPhase.EVIDENCE, InvestigationPhase.REVIEW, InvestigationPhase.ESCALATED},
    InvestigationPhase.EVIDENCE: {InvestigationPhase.REVIEW, InvestigationPhase.INVESTIGATE},
    InvestigationPhase.REVIEW: {InvestigationPhase.DECIDE, InvestigationPhase.INVESTIGATE, InvestigationPhase.ESCALATED},
    InvestigationPhase.DECIDE: {InvestigationPhase.REPORT, InvestigationPhase.CLOSED},
    InvestigationPhase.REPORT: {InvestigationPhase.CLOSED},
    InvestigationPhase.CLOSED: set(),
    InvestigationPhase.ESCALATED: {InvestigationPhase.INVESTIGATE, InvestigationPhase.CLOSED},
}

PHASE_TO_EVENT: Dict[InvestigationPhase, EventType] = {
    InvestigationPhase.ALERT: EventType.INVESTIGATION_CREATED,
    InvestigationPhase.TRIAGE: EventType.INVESTIGATION_STARTED,
    InvestigationPhase.INVESTIGATE: EventType.INVESTIGATION_AGENT_DISPATCHED,
    InvestigationPhase.EVIDENCE: EventType.INVESTIGATION_EVIDENCE_COLLECTED,
    InvestigationPhase.REVIEW: EventType.INVESTIGATION_FINDING_ADDED,
    InvestigationPhase.DECIDE: EventType.INVESTIGATION_VERDICT_REACHED,
    InvestigationPhase.REPORT: EventType.SAR_GENERATED,
    InvestigationPhase.CLOSED: EventType.INVESTIGATION_CLOSED,
    InvestigationPhase.ESCALATED: EventType.INVESTIGATION_ESCALATED,
}


class InvalidTransitionError(Exception):
    pass


class InvestigationLifecycle:
    """State machine for investigation lifecycle management."""

    def __init__(self, case_id: str, initial_phase: InvestigationPhase = InvestigationPhase.ALERT):
        self.case_id = case_id
        self._current_phase = initial_phase
        self._history: List[InvestigationPhase] = [initial_phase]
        self._event_store = get_event_store()

    @property
    def current_phase(self) -> InvestigationPhase:
        return self._current_phase

    @property
    def history(self) -> List[InvestigationPhase]:
        return list(self._history)

    @property
    def is_terminal(self) -> bool:
        return self._current_phase == InvestigationPhase.CLOSED

    def can_transition(self, target: InvestigationPhase) -> bool:
        """Check if a transition is valid without executing it."""
        return target in VALID_TRANSITIONS.get(self._current_phase, set())

    def valid_next_phases(self) -> Set[InvestigationPhase]:
        """Get all valid next phases from current state."""
        return VALID_TRANSITIONS.get(self._current_phase, set())

    def transition(
        self,
        target: InvestigationPhase,
        agent_name: str = "",
        data: Optional[Dict] = None,
        reasoning: Optional[List[str]] = None,
        confidence: float = 0.0,
    ) -> InvestigationEvent:
        """Execute a state transition, emitting an event."""
        if not self.can_transition(target):
            raise InvalidTransitionError(
                f"Invalid transition: {self._current_phase.value} → {target.value}. "
                f"Valid: {[p.value for p in self.valid_next_phases()]}"
            )

        previous = self._current_phase
        self._current_phase = target
        self._history.append(target)

        event_type = PHASE_TO_EVENT.get(target, EventType.SYSTEM_ALERT)
        event = InvestigationEvent(
            event_type=event_type,
            case_id=self.case_id,
            agent_name=agent_name,
            data={
                "from_phase": previous.value,
                "to_phase": target.value,
                **(data or {}),
            },
            reasoning_chain=reasoning or [],
            confidence=confidence,
        )

        stored = self._event_store.append(event)
        logger.info(
            "Investigation phase transition",
            case_id=self.case_id,
            from_phase=previous.value,
            to_phase=target.value,
        )

        return stored

    @classmethod
    def from_events(cls, case_id: str, events: List[InvestigationEvent]) -> "InvestigationLifecycle":
        """Reconstruct lifecycle state by replaying events."""
        lifecycle = cls(case_id, InvestigationPhase.ALERT)

        for event in events:
            target_phase_str = event.data.get("to_phase")
            if target_phase_str:
                try:
                    target = InvestigationPhase(target_phase_str)
                    if lifecycle.can_transition(target):
                        lifecycle._current_phase = target
                        lifecycle._history.append(target)
                except ValueError:
                    pass

        return lifecycle
