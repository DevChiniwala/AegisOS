import asyncio
from typing import Dict, List, Set
from collections import defaultdict
from core.schemas.events import EventEnvelope, EventType
from .bus import EventBus, EventHandler
import structlog

logger = structlog.get_logger(__name__)


class InMemoryEventBus:
    def __init__(self) -> None:
        self.handlers: Dict[str, Set[EventHandler]] = defaultdict(set)
        self.event_history: List[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        self.event_history.append(event)
        
        handlers_to_call = set()
        
        # Get exact match handlers
        if event.event_type.value in self.handlers:
            handlers_to_call.update(self.handlers[event.event_type.value])
            
        # Get wildcard handlers
        if "*" in self.handlers:
            handlers_to_call.update(self.handlers["*"])

        if not handlers_to_call:
            logger.debug("no_handlers_for_event", event_type=event.event_type)
            return

        # Execute handlers concurrently
        tasks = [asyncio.create_task(self._safe_execute(handler, event)) for handler in handlers_to_call]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, handler: EventHandler, event: EventEnvelope) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error("event_handler_failed", event_type=event.event_type, error=str(e))

    async def subscribe(self, event_type: EventType | str, handler: EventHandler) -> None:
        key = event_type.value if isinstance(event_type, EventType) else event_type
        self.handlers[key].add(handler)

    async def unsubscribe(self, event_type: EventType | str, handler: EventHandler) -> None:
        key = event_type.value if isinstance(event_type, EventType) else event_type
        if key in self.handlers and handler in self.handlers[key]:
            self.handlers[key].remove(handler)
