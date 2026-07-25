"""
Stream Consumers — InMemory and Redis Stream implementations.
"""
import asyncio
import json
from typing import AsyncIterator, Protocol

from core.schemas.events import EventEnvelope
from core.utils.logging import get_logger

logger = get_logger(__name__)


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
        self._running = False

    async def _ensure_group(self):
        try:
            await self.redis.xgroup_create(
                self.stream_name, self.group_name, id="0", mkstream=True
            )
        except Exception:
            pass

    async def consume(self) -> AsyncIterator[EventEnvelope]:
        await self._ensure_group()
        self._running = True

        while self._running:
            try:
                messages = await self.redis.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},
                    count=10,
                    block=5000,
                )
            except Exception as e:
                logger.error("Redis stream read failed", error=str(e))
                await asyncio.sleep(1)
                continue

            if not messages:
                continue

            for stream, entries in messages:
                for msg_id, data in entries:
                    try:
                        payload_key = b"payload" if b"payload" in data else "payload"
                        raw = data.get(payload_key, data.get(b"data", b"{}"))
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8")
                        parsed = json.loads(raw)
                        event = EventEnvelope(**parsed)
                        yield event
                        await self.redis.xack(self.stream_name, self.group_name, msg_id)
                    except Exception as e:
                        logger.error("Failed to parse stream message", msg_id=msg_id, error=str(e))
                        await self.redis.xack(self.stream_name, self.group_name, msg_id)

    def stop(self):
        self._running = False
