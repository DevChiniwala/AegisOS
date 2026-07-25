"""
Temporal Worker process for AegisOS investigation workflows.

Run with: python -m services.temporal.worker
Or via CLI: aegis temporal-worker
"""

import asyncio
import signal
from typing import Optional

from temporalio.client import Client
from temporalio.worker import Worker

from core.utils.logging import get_logger
from services.temporal.activities import (
    run_compliance_and_decision,
    run_deep_investigation,
    run_triage_agents,
)
from services.temporal.workflows import TASK_QUEUE, InvestigationWorkflow

logger = get_logger(__name__)

_worker: Optional[Worker] = None


async def create_worker(
    host: str = "localhost:7233",
    namespace: str = "default",
    task_queue: str = TASK_QUEUE,
) -> Worker:
    """Create a Temporal Worker connected to the specified server."""
    client = await Client.connect(host, namespace=namespace)

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[InvestigationWorkflow],
        activities=[
            run_triage_agents,
            run_deep_investigation,
            run_compliance_and_decision,
        ],
    )

    return worker


async def run_worker(
    host: str = "localhost:7233",
    namespace: str = "default",
    task_queue: str = TASK_QUEUE,
) -> None:
    """Run the Temporal Worker until shutdown signal."""
    global _worker

    logger.info(
        "Starting Temporal worker",
        host=host,
        namespace=namespace,
        task_queue=task_queue,
    )

    _worker = await create_worker(host, namespace, task_queue)

    shutdown_event = asyncio.Event()

    def _signal_handler():
        logger.info("Shutdown signal received")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass

    async with _worker:
        logger.info("Temporal worker running", task_queue=task_queue)
        await shutdown_event.wait()

    logger.info("Temporal worker stopped")


def main():
    """Entry point for temporal worker."""
    from core.config.settings import get_settings

    settings = get_settings()
    temporal = settings.temporal

    asyncio.run(run_worker(
        host=temporal.host,
        namespace=temporal.namespace,
        task_queue=temporal.task_queue,
    ))


if __name__ == "__main__":
    main()
