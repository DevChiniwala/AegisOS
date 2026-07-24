"""Base agent infrastructure with tool-calling capability."""
from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable, Dict, List, Optional
from dataclasses import dataclass, field
from core.schemas.investigation import InvestigationCase, Finding
from core.schemas.transaction import TransactionCreate


@dataclass
class AgentTool:
    name: str
    description: str
    function: Callable[..., Awaitable[Any]]
    parameters: Dict[str, Any] = field(default_factory=dict)


class ToolKit:
    """Collection of tools available to investigation agents."""

    def __init__(self):
        self._tools: Dict[str, AgentTool] = {}

    def register(self, tool: AgentTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[AgentTool]:
        return self._tools.get(name)

    @property
    def tools(self) -> List[AgentTool]:
        return list(self._tools.values())

    def tool_descriptions(self) -> str:
        return "\n".join(f"- {t.name}: {t.description}" for t in self._tools.values())

    async def execute(self, name: str, **kwargs) -> Any:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return await tool.function(**kwargs)


class AgentMemory:
    """Per-agent short-term memory across investigation steps."""

    def __init__(self, max_items: int = 50):
        self._items: List[Dict[str, Any]] = []
        self._max_items = max_items

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None):
        entry = {"key": key, "value": value, "metadata": metadata or {}}
        self._items.append(entry)
        if len(self._items) > self._max_items:
            self._items = self._items[-self._max_items:]

    def recall(self, key: str) -> Optional[Any]:
        for item in reversed(self._items):
            if item["key"] == key:
                return item["value"]
        return None

    def recall_all(self, key: str) -> List[Any]:
        return [item["value"] for item in self._items if item["key"] == key]

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        return [
            item for item in self._items
            if query_lower in str(item["value"]).lower() or query_lower in item["key"].lower()
        ]

    def clear(self):
        self._items.clear()

    @property
    def size(self) -> int:
        return len(self._items)


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
    toolkit: Optional[ToolKit] = None


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description
        self.memory = AgentMemory()
        self._toolkit: Optional[ToolKit] = None

    def set_toolkit(self, toolkit: ToolKit):
        self._toolkit = toolkit

    async def use_tool(self, name: str, **kwargs) -> Any:
        if not self._toolkit:
            raise RuntimeError(f"Agent {self.name} has no toolkit assigned")
        return await self._toolkit.execute(name, **kwargs)

    @abstractmethod
    async def investigate(self, context: InvestigationContext) -> Finding:
        pass

    def system_prompt(self) -> str:
        tools_desc = self._toolkit.tool_descriptions() if self._toolkit else "No tools available."
        return (
            f"You are {self.name}, a {self.role}.\n"
            f"Your mission: {self.description}\n\n"
            f"Available tools:\n{tools_desc}\n\n"
            "Provide structured analysis with confidence scores and evidence citations."
        )
