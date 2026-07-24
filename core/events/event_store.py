"""
Append-only Event Store for investigation audit trails.

All investigation actions are stored as immutable events.
State is reconstructed by replaying the event stream.
"""
import json
import threading
from typing import Callable, Dict, List, Optional
from pathlib import Path

from core.events.models import InvestigationEvent, EventType
from core.utils.logging import get_logger

logger = get_logger(__name__)


class EventStore:
    """Append-only event store with in-memory and file-backed persistence."""

    def __init__(self, storage_path: Optional[str] = None):
        self._events: Dict[str, List[InvestigationEvent]] = {}
        self._global_sequence: int = 0
        self._lock = threading.Lock()
        self._subscribers: List[Callable[[InvestigationEvent], None]] = []
        self._storage_path = Path(storage_path) if storage_path else None

        if self._storage_path:
            self._storage_path.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()

    def append(self, event: InvestigationEvent) -> InvestigationEvent:
        """Append an event to the store. Returns the event with sequence number assigned."""
        with self._lock:
            self._global_sequence += 1
            event = InvestigationEvent(
                event_id=event.event_id,
                event_type=event.event_type,
                case_id=event.case_id,
                timestamp=event.timestamp,
                agent_name=event.agent_name,
                data=event.data,
                reasoning_chain=event.reasoning_chain,
                confidence=event.confidence,
                metadata=event.metadata,
                sequence_number=self._global_sequence,
            )

            if event.case_id not in self._events:
                self._events[event.case_id] = []
            self._events[event.case_id].append(event)

            if self._storage_path:
                self._persist_event(event)

        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.warning("Event subscriber error", error=str(e))

        return event

    def get_stream(self, case_id: str) -> List[InvestigationEvent]:
        """Get the full event stream for a case."""
        return list(self._events.get(case_id, []))

    def get_events_by_type(self, case_id: str, event_type: EventType) -> List[InvestigationEvent]:
        """Get events of a specific type for a case."""
        return [e for e in self._events.get(case_id, []) if e.event_type == event_type]

    def get_latest(self, case_id: str) -> Optional[InvestigationEvent]:
        """Get the most recent event for a case."""
        events = self._events.get(case_id, [])
        return events[-1] if events else None

    def get_all_cases(self) -> List[str]:
        """Get all case IDs in the store."""
        return list(self._events.keys())

    def count(self, case_id: Optional[str] = None) -> int:
        """Count events, optionally for a specific case."""
        if case_id:
            return len(self._events.get(case_id, []))
        return sum(len(events) for events in self._events.values())

    def subscribe(self, callback: Callable[[InvestigationEvent], None]):
        """Subscribe to new events."""
        self._subscribers.append(callback)

    def replay(self, case_id: str, up_to_sequence: Optional[int] = None) -> List[InvestigationEvent]:
        """Replay events up to a given sequence number."""
        events = self._events.get(case_id, [])
        if up_to_sequence is not None:
            return [e for e in events if e.sequence_number <= up_to_sequence]
        return list(events)

    def _persist_event(self, event: InvestigationEvent):
        """Persist event to disk as JSONL."""
        file_path = self._storage_path / f"{event.case_id}.jsonl"
        with open(file_path, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def _load_from_disk(self):
        """Load events from disk on startup."""
        if not self._storage_path or not self._storage_path.exists():
            return

        for file_path in self._storage_path.glob("*.jsonl"):
            case_id = file_path.stem
            self._events[case_id] = []
            with open(file_path) as f:
                for line in f:
                    if line.strip():
                        event = InvestigationEvent.from_dict(json.loads(line))
                        self._events[case_id].append(event)
                        self._global_sequence = max(self._global_sequence, event.sequence_number)


_event_store: Optional[EventStore] = None


def get_event_store(storage_path: Optional[str] = None) -> EventStore:
    """Get the global event store singleton."""
    global _event_store
    if _event_store is None:
        _event_store = EventStore(storage_path=storage_path)
    return _event_store
