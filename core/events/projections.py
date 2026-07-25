"""
Event Projections — Materializers that reconstruct state from event streams.

Projections transform the raw event stream into useful read models
(current case state, agent timeline, evidence summary, etc.)
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.events.models import EventType, InvestigationEvent


@dataclass
class CaseState:
    """Projected current state of an investigation case."""
    case_id: str
    status: str = "created"
    verdict: str = ""
    confidence: float = 0.0
    agents_completed: List[str] = field(default_factory=list)
    agents_in_progress: List[str] = field(default_factory=list)
    findings_count: int = 0
    evidence_count: int = 0
    risk_score: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AgentTimeline:
    """Projected timeline of agent activity."""
    case_id: str
    entries: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EvidenceSummary:
    """Projected evidence collected during investigation."""
    case_id: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    total_confidence: float = 0.0


class CaseStateProjection:
    """Projects the current state of a case from its event stream."""

    def project(self, events: List[InvestigationEvent]) -> CaseState:
        if not events:
            return CaseState(case_id="")

        case_id = events[0].case_id
        state = CaseState(case_id=case_id)

        for event in events:
            state.last_updated = event.timestamp
            self._apply(state, event)

        return state

    def _apply(self, state: CaseState, event: InvestigationEvent):
        if event.event_type == EventType.INVESTIGATION_CREATED:
            state.status = "created"
            state.risk_score = event.data.get("risk_score", 0.0)

        elif event.event_type == EventType.INVESTIGATION_STARTED:
            state.status = "in_progress"
            state.started_at = event.timestamp

        elif event.event_type == EventType.INVESTIGATION_AGENT_DISPATCHED:
            agent = event.agent_name
            if agent and agent not in state.agents_in_progress:
                state.agents_in_progress.append(agent)

        elif event.event_type == EventType.INVESTIGATION_AGENT_COMPLETED:
            agent = event.agent_name
            if agent in state.agents_in_progress:
                state.agents_in_progress.remove(agent)
            if agent not in state.agents_completed:
                state.agents_completed.append(agent)

        elif event.event_type == EventType.INVESTIGATION_FINDING_ADDED:
            state.findings_count += 1

        elif event.event_type == EventType.INVESTIGATION_EVIDENCE_COLLECTED:
            state.evidence_count += event.data.get("items_count", 1)

        elif event.event_type == EventType.INVESTIGATION_VERDICT_REACHED:
            state.verdict = event.data.get("verdict", "")
            state.confidence = event.confidence
            state.recommendations = event.data.get("recommendations", [])

        elif event.event_type == EventType.INVESTIGATION_CLOSED:
            state.status = "closed"
            state.completed_at = event.timestamp

        elif event.event_type == EventType.INVESTIGATION_ESCALATED:
            state.status = "escalated"


class AgentTimelineProjection:
    """Projects a timeline of agent activity from events."""

    def project(self, events: List[InvestigationEvent]) -> AgentTimeline:
        if not events:
            return AgentTimeline(case_id="")

        case_id = events[0].case_id
        timeline = AgentTimeline(case_id=case_id)

        for event in events:
            if event.event_type in (
                EventType.INVESTIGATION_AGENT_DISPATCHED,
                EventType.INVESTIGATION_AGENT_COMPLETED,
                EventType.INVESTIGATION_FINDING_ADDED,
            ):
                timeline.entries.append({
                    "timestamp": event.timestamp.isoformat(),
                    "agent": event.agent_name,
                    "event": event.event_type.value,
                    "confidence": event.confidence,
                    "reasoning": event.reasoning_chain[:3],
                })

        return timeline


class EvidenceSummaryProjection:
    """Projects an evidence summary from events."""

    def project(self, events: List[InvestigationEvent]) -> EvidenceSummary:
        if not events:
            return EvidenceSummary(case_id="")

        case_id = events[0].case_id
        summary = EvidenceSummary(case_id=case_id)

        for event in events:
            if event.event_type == EventType.INVESTIGATION_EVIDENCE_COLLECTED:
                items = event.data.get("items", [])
                for item in items:
                    summary.items.append(item)

            if event.event_type == EventType.INVESTIGATION_FINDING_ADDED:
                summary.items.append({
                    "type": "finding",
                    "agent": event.agent_name,
                    "description": event.data.get("description", ""),
                    "confidence": event.confidence,
                })

        if summary.items:
            confidences = [i.get("confidence", 0) for i in summary.items if "confidence" in i]
            summary.total_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return summary
