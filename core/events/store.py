from typing import List, Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import EventStoreRecord
from core.schemas.events import InvestigationEvent


class EventStore(Protocol):
    async def append(self, event: InvestigationEvent) -> None:
        ...

    async def get_events_for_aggregate(self, aggregate_id: str) -> List[InvestigationEvent]:
        ...


class PostgresEventStore(EventStore):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def append(self, event: InvestigationEvent) -> None:
        """Appends a new immutable event to the store."""
        record = EventStoreRecord(
            event_id=str(event.event_id),
            aggregate_id=event.case_id,
            event_type=event.event_type,
            timestamp=event.timestamp,
            payload_json=event.model_dump(mode='json'),
            agent_name=event.agent_name
        )
        self.session.add(record)
        await self.session.commit()

    async def get_events_for_aggregate(self, aggregate_id: str) -> List[InvestigationEvent]:
        """Retrieves all events for a specific case (aggregate) in order."""
        stmt = (
            select(EventStoreRecord)
            .where(EventStoreRecord.aggregate_id == aggregate_id)
            .order_by(EventStoreRecord.sequence_id.asc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        
        events = []
        for r in records:
            # We reconstruct the InvestigationEvent from the stored JSON payload
            events.append(InvestigationEvent(**r.payload_json))
        return events
