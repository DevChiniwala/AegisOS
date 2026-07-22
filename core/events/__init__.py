import logging
from .bus import EventBus, EventHandler
from .memory_bus import InMemoryEventBus
from .redis_bus import RedisEventBus
from core.config.settings import get_settings

logger = logging.getLogger(__name__)

_event_bus_instance: EventBus | None = None


async def get_event_bus() -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is not None:
        return _event_bus_instance

    settings = get_settings()
    if settings.features.enable_streaming and settings.redis.url:
        bus = RedisEventBus(settings.redis.url)
        await bus.connect()
        logger.info("Redis EventBus connected")
        _event_bus_instance = bus
    else:
        _event_bus_instance = InMemoryEventBus()
        logger.info("Using InMemory EventBus")

    return _event_bus_instance


async def shutdown_event_bus():
    global _event_bus_instance
    if _event_bus_instance and hasattr(_event_bus_instance, 'disconnect'):
        await _event_bus_instance.disconnect()
    _event_bus_instance = None


__all__ = [
    "EventBus",
    "EventHandler",
    "InMemoryEventBus",
    "RedisEventBus",
    "get_event_bus",
    "shutdown_event_bus",
]
