from .bus import EventBus, EventHandler
from .memory_bus import InMemoryEventBus
from .redis_bus import RedisEventBus
from core.config.settings import get_settings

def get_event_bus() -> EventBus:
    settings = get_settings()
    if settings.features.enable_streaming and settings.redis.url:
        return RedisEventBus(settings.redis.url)
    return InMemoryEventBus()

__all__ = [
    "EventBus",
    "EventHandler",
    "InMemoryEventBus",
    "RedisEventBus",
    "get_event_bus",
]
