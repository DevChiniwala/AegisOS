"""
Temporal Investigation Client — interface for starting and managing durable investigations.

Usage:
    client = await TemporalInvestigationClient.connect()
    workflow_id = await client.start_investigation(
        case_id="CASE-ABC123",
        transaction={"amount": 15000, "sender_id": "user_456"},
        risk_score=0.87,
        features={"is_new_device": 1.0, "amount_zscore": 3.2},
    )
    # Later: analyst signals
    await client.signal_approve(workflow_id, notes="Verified legitimate")
    # Or get result
    result = await client.get_result(workflow_id)
"""

from typing import Any, Dict, Optional

from temporalio.client import Client

from core.utils.logging import get_logger
from services.temporal.workflows import (
    TASK_QUEUE,
    InvestigationInput,
    InvestigationResult,
    InvestigationWorkflow,
)

logger = get_logger(__name__)


class TemporalInvestigationClient:
    """Client for managing durable investigation workflows via Temporal."""

    def __init__(self, client: Client, task_queue: str = TASK_QUEUE):
        self._client = client
        self._task_queue = task_queue

    @classmethod
    async def connect(
        cls,
        host: str = "localhost:7233",
        namespace: str = "default",
        task_queue: str = TASK_QUEUE,
    ) -> "TemporalInvestigationClient":
        """Connect to Temporal server and return a client instance."""
        client = await Client.connect(host, namespace=namespace)
        return cls(client, task_queue)

    async def start_investigation(
        self,
        case_id: str,
        transaction: Dict[str, Any],
        risk_score: float,
        features: Dict[str, float],
        investigation_plan: Optional[list] = None,
    ) -> str:
        """Start a durable investigation workflow. Returns workflow ID."""
        workflow_id = f"investigation-{case_id}"

        handle = await self._client.start_workflow(
            InvestigationWorkflow.run,
            InvestigationInput(
                case_id=case_id,
                transaction=transaction,
                risk_score=risk_score,
                features=features,
                investigation_plan=investigation_plan or [],
            ),
            id=workflow_id,
            task_queue=self._task_queue,
        )

        logger.info(
            "Investigation workflow started",
            case_id=case_id,
            workflow_id=workflow_id,
            risk_score=risk_score,
        )

        return handle.id

    async def get_result(self, workflow_id: str) -> InvestigationResult:
        """Wait for and return the investigation result."""
        handle = self._client.get_workflow_handle(workflow_id)
        return await handle.result()

    async def get_result_by_case(self, case_id: str) -> InvestigationResult:
        """Get result by case ID (convenience wrapper)."""
        return await self.get_result(f"investigation-{case_id}")

    async def signal_approve(self, workflow_id: str, notes: str = "") -> None:
        """Signal analyst approval to a waiting investigation."""
        handle = self._client.get_workflow_handle(workflow_id)
        await handle.signal(InvestigationWorkflow.analyst_approve, notes)
        logger.info("Sent approve signal", workflow_id=workflow_id)

    async def signal_reject(self, workflow_id: str, notes: str = "") -> None:
        """Signal analyst rejection — clears the investigation."""
        handle = self._client.get_workflow_handle(workflow_id)
        await handle.signal(InvestigationWorkflow.analyst_reject, notes)
        logger.info("Sent reject signal", workflow_id=workflow_id)

    async def signal_escalate(self, workflow_id: str, notes: str = "") -> None:
        """Signal analyst escalation."""
        handle = self._client.get_workflow_handle(workflow_id)
        await handle.signal(InvestigationWorkflow.analyst_escalate, notes)
        logger.info("Sent escalate signal", workflow_id=workflow_id)

    async def add_evidence(self, workflow_id: str, evidence: Dict[str, Any]) -> None:
        """Add evidence to an in-progress investigation."""
        handle = self._client.get_workflow_handle(workflow_id)
        await handle.signal(InvestigationWorkflow.add_evidence, evidence)
        logger.info("Sent evidence signal", workflow_id=workflow_id, evidence_type=evidence.get("type"))

    async def query_status(self, workflow_id: str) -> Dict[str, Any]:
        """Query current investigation status without blocking."""
        handle = self._client.get_workflow_handle(workflow_id)
        return await handle.query(InvestigationWorkflow.get_status)

    async def cancel(self, workflow_id: str) -> None:
        """Cancel a running investigation workflow."""
        handle = self._client.get_workflow_handle(workflow_id)
        await handle.cancel()
        logger.info("Investigation cancelled", workflow_id=workflow_id)

    async def terminate(self, workflow_id: str, reason: str = "") -> None:
        """Terminate a running investigation (hard stop)."""
        handle = self._client.get_workflow_handle(workflow_id)
        await handle.terminate(reason=reason)
        logger.info("Investigation terminated", workflow_id=workflow_id, reason=reason)
