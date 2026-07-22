"""
Stream Processor Engine.
"""
import asyncio
from core.schemas.events import EventEnvelope
from core.schemas.transaction import TransactionCreate
from core.utils.logging import get_logger
from services.streaming.consumers import EventConsumer
from services.streaming.producers import EventProducer

logger = get_logger(__name__)

class StreamProcessor:
    def __init__(self, consumer: EventConsumer, producer: EventProducer, concurrency: int = 10):
        self.consumer = consumer
        self.producer = producer
        self.semaphore = asyncio.Semaphore(concurrency)
        self.is_running = False
        self.metrics = {"processed": 0, "errors": 0}

    async def start(self):
        """Start consuming from event bus."""
        self.is_running = True
        logger.info("StreamProcessor started.")
        try:
            async for event in self.consumer.consume():
                if not self.is_running:
                    break
                await self._process_with_semaphore(event)
        except Exception as e:
            logger.error(f"StreamProcessor error: {e}")
            self.is_running = False

    async def stop(self):
        """Graceful shutdown."""
        self.is_running = False
        logger.info("StreamProcessor stopped.")

    async def _process_with_semaphore(self, event: EventEnvelope):
        async with self.semaphore:
            try:
                await self.process_transaction(event)
                self.metrics["processed"] += 1
            except Exception as e:
                logger.error(f"Error processing event {event.id}: {e}")
                self.metrics["errors"] += 1
                # send to DLQ
                # await self.producer.produce_dlq(event)

    async def process_transaction(self, event: EventEnvelope):
        """Full scoring pipeline."""
        # 1. Parse transaction
        # data = event.data
        # 2. Feature extraction (mocked)
        # 3. Risk scoring (mocked)
        # 4. Trigger investigation if high risk
        # 5. Publish result event
        logger.info(f"Processing transaction event {event.id}")
        await asyncio.sleep(0.01) # Simulate processing
        
        # Publish processed event
        await self.producer.produce(EventEnvelope(
            id=f"res_{event.id}",
            event_type="TRANSACTION_SCORED",
            source="streaming_engine",
            data={"status": "scored", "original_id": event.id}
        ))
