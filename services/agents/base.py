from abc import ABC, abstractmethod
from typing import Any, Dict, List
from dataclasses import dataclass, field
from core.schemas.investigation import InvestigationCase, Finding
from core.schemas.transaction import TransactionCreate

@dataclass
class InvestigationContext:
    case: InvestigationCase
    transaction: TransactionCreate
    features: Dict[str, Any]
    risk_score: float
    graph_data: Dict[str, Any] = field(default_factory=dict)
    behavioral_data: Dict[str, Any] = field(default_factory=dict)
    memory_data: Dict[str, Any] = field(default_factory=dict)
    previous_findings: List[Finding] = field(default_factory=list)

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description

    @abstractmethod
    async def investigate(self, context: InvestigationContext) -> Finding:
        """Execute the agent's investigation logic and return a Finding."""
        pass
