from typing import Protocol, Callable, Awaitable, Any
from core.schemas.events import EventEnvelope, EventType

EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class EventBus(Protocol):
    async def publish(self, event: EventEnvelope) -> None:
        """Publish an event to the bus."""
        ...

    async def subscribe(self, event_type: EventType | str, handler: EventHandler) -> None:
        """Subscribe to an event type. Use '*' for wildcard subscriptions."""
        ...

    async def unsubscribe(self, event_type: EventType | str, handler: EventHandler) -> None:
        """Unsubscribe from an event type."""
        ...
