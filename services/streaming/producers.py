"""
Stream Producers.
"""
from typing import Protocol
import asyncio
from core.schemas.events import EventEnvelope

class EventProducer(Protocol):
    async def produce(self, event: EventEnvelope) -> None:
        ...

class InMemoryProducer(EventProducer):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        
    async def produce(self, event: EventEnvelope) -> None:
        await self.queue.put(event)

class RedisStreamProducer(EventProducer):
    def __init__(self, redis_client, stream_name: str):
        self.redis = redis_client
        self.stream_name = stream_name

    async def produce(self, event: EventEnvelope) -> None:
        # Implementation for producing to Redis Streams
        # await self.redis.xadd(self.stream_name, event.model_dump())
        pass
