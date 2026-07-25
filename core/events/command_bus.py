import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Generic, Protocol, Type, TypeVar

from pydantic import BaseModel

from core.schemas.events import InvestigationEvent

from .store import EventStore


def utc_now():
    return datetime.now(timezone.utc)

C = TypeVar('C', bound=BaseModel)

class CommandHandler(Generic[C], Protocol):
    async def handle(self, command: C) -> None:
        ...

class CommandBus:
    """
    Central bus for dispatching CQRS commands.
    Translates state-mutating intents into immutable InvestigationEvents.
    """
    def __init__(self, event_store: EventStore):
        self._handlers: Dict[Type[BaseModel], CommandHandler] = {}
        self.event_store = event_store

    def register(self, command_type: Type[BaseModel], handler: CommandHandler) -> None:
        self._handlers[command_type] = handler

    async def dispatch(self, command: BaseModel) -> None:
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command type: {type(command)}")
        await handler.handle(command)


# Example Commands for the Investigation Domain
class StartInvestigationCommand(BaseModel):
    transaction_id: str
    priority: str
    initial_risk_score: float

class AddEvidenceCommand(BaseModel):
    case_id: str
    agent_name: str
    finding_type: str
    description: str
    confidence: float
    evidence_data: Dict[str, Any]


# Corresponding Handlers
class StartInvestigationHandler:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    async def handle(self, command: StartInvestigationCommand) -> None:
        # Generate new case ID
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        
        event = InvestigationEvent(
            case_id=case_id,
            event_type="INVESTIGATION_STARTED",
            payload={
                "transaction_id": command.transaction_id,
                "priority": command.priority,
                "initial_risk_score": command.initial_risk_score
            }
        )
        await self.event_store.append(event)


class AddEvidenceHandler:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    async def handle(self, command: AddEvidenceCommand) -> None:
        event = InvestigationEvent(
            case_id=command.case_id,
            event_type="EVIDENCE_FOUND",
            agent_name=command.agent_name,
            confidence=command.confidence,
            payload={
                "finding_type": command.finding_type,
                "description": command.description,
                "evidence_data": command.evidence_data
            }
        )
        await self.event_store.append(event)
