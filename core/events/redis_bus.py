import json
import asyncio
from typing import Optional
from redis.asyncio import Redis
from core.schemas.events import EventEnvelope, EventType
from core.exceptions import EventBusError
from .bus import EventBus, EventHandler
import structlog

logger = structlog.get_logger(__name__)


class RedisEventBus:
    def __init__(self, redis_url: str, group_name: str = "aegis_group"):
        self.redis_url = redis_url
        self.group_name = group_name
        self.redis: Optional[Redis] = None
        self.handlers = {}
        self.running = False
        self._listen_task = None

    async def connect(self):
        self.redis = Redis.from_url(self.redis_url, decode_responses=True)
        self.running = True
        self._listen_task = asyncio.create_task(self._listen())

    async def disconnect(self):
        self.running = False
        if self._listen_task:
            self._listen_task.cancel()
        if self.redis:
            await self.redis.close()

    async def publish(self, event: EventEnvelope) -> None:
        if not self.redis:
            raise EventBusError("RedisEventBus not connected")
            
        stream_name = f"events:{event.event_type.value}"
        payload_str = event.model_dump_json()
        await self.redis.xadd(stream_name, {"payload": payload_str})
        
    async def subscribe(self, event_type: EventType | str, handler: EventHandler) -> None:
        key = event_type.value if isinstance(event_type, EventType) else event_type
        if key not in self.handlers:
            self.handlers[key] = set()
            
            # Create consumer group if needed
            stream_name = f"events:{key}"
            try:
                if self.redis:
                    await self.redis.xgroup_create(stream_name, self.group_name, id="0", mkstream=True)
            except Exception as e:
                # Group might already exist, which is fine
                pass
                
        self.handlers[key].add(handler)

    async def unsubscribe(self, event_type: EventType | str, handler: EventHandler) -> None:
        key = event_type.value if isinstance(event_type, EventType) else event_type
        if key in self.handlers and handler in self.handlers[key]:
            self.handlers[key].remove(handler)

    async def _listen(self):
        while self.running:
            if not self.handlers:
                await asyncio.sleep(1)
                continue
                
            try:
                streams = {f"events:{k}": ">" for k in self.handlers.keys()}
                messages = await self.redis.xreadgroup(
                    self.group_name, 
                    "consumer_1", 
                    streams, 
                    count=10, 
                    block=1000
                )
                
                for stream, msgs in messages:
                    event_type = stream.split(":")[1]
                    for msg_id, data in msgs:
                        try:
                            payload = json.loads(data["payload"])
                            event = EventEnvelope(**payload)
                            
                            handlers_to_call = self.handlers.get(event_type, set())
                            if "*" in self.handlers:
                                handlers_to_call = handlers_to_call.union(self.handlers["*"])
                                
                            for handler in handlers_to_call:
                                try:
                                    await handler(event)
                                except Exception as e:
                                    logger.error("redis_event_handler_failed", event_type=event_type, error=str(e))
                                    
                            await self.redis.xack(stream, self.group_name, msg_id)
                        except Exception as e:
                            logger.error("redis_event_parse_failed", error=str(e))
                            
            except Exception as e:
                logger.error("redis_listen_error", error=str(e))
                await asyncio.sleep(1)
