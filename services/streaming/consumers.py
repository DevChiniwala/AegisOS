"""
Stream Consumers.
"""
from typing import Protocol, AsyncIterator
import asyncio
from core.schemas.events import EventEnvelope

class EventConsumer(Protocol):
    def consume(self) -> AsyncIterator[EventEnvelope]:
        ...

class InMemoryConsumer(EventConsumer):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        
    async def consume(self) -> AsyncIterator[EventEnvelope]:
        while True:
            event = await self.queue.get()
            yield event
            self.queue.task_done()

class RedisStreamConsumer(EventConsumer):
    def __init__(self, redis_client, stream_name: str, group_name: str, consumer_name: str):
        self.redis = redis_client
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name

    async def consume(self) -> AsyncIterator[EventEnvelope]:
        # Implementation for consuming from Redis Streams
        # Example pseudo-code:
        # while True:
        #     messages = await self.redis.xreadgroup(...)
        #     for msg in messages:
        #         yield parse_event(msg)
        yield EventEnvelope(id="test", event_type="TEST", source="test", data={})
