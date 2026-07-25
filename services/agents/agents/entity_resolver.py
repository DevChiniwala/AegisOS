"""Entity Resolver Agent — Links identities across devices, IPs, and accounts."""
import uuid

from core.schemas.investigation import Finding
from core.utils.helpers import utc_now

from ..base import BaseAgent, InvestigationContext


class EntityResolverAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="EntityResolver",
            role="Identity Analyst",
            description="Resolves and links entities across multiple identity dimensions (devices, IPs, emails, accounts) to uncover hidden connections",
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        tx = context.transaction
        graph_data = context.graph_data
        findings = []
        confidence = 0.5
        linked_entities = []

        sender_id = tx.sender_id if hasattr(tx, "sender_id") else ""
        receiver_id = tx.receiver_id if hasattr(tx, "receiver_id") else ""

        shared = graph_data.get("shared_entities", {})
        shared_devices = shared.get("shared_devices", [])
        shared_ips = shared.get("shared_ips", [])
        shared_emails = shared.get("shared_emails", [])

        if shared_devices:
            findings.append(f"Sender and receiver share {len(shared_devices)} device(s)")
            linked_entities.extend(shared_devices)
            confidence += 0.15

        if shared_ips:
            findings.append(f"Common IP addresses detected: {len(shared_ips)}")
            linked_entities.extend(shared_ips)
            confidence += 0.1

        if shared_emails:
            findings.append(f"Shared email domains: {len(shared_emails)}")
            confidence += 0.05

        neighbors = graph_data.get("neighbors", [])
        mutual = [n for n in neighbors if n.get("connected_to_receiver")]
        if mutual:
            findings.append(f"{len(mutual)} mutual connections between parties")
            confidence += 0.1

        if sender_id and receiver_id and sender_id[:8] == receiver_id[:8]:
            findings.append("WARNING: Sender/receiver share ID prefix — possible self-transaction")
            confidence += 0.2

        confidence = min(confidence, 0.99)
        desc = "; ".join(findings) if findings else "No cross-entity linkage detected"
        if linked_entities:
            desc += f" | Linked entities: {len(linked_entities)}"

        self.memory.store("linked_entities", linked_entities)

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Entity Resolution Analysis",
            description=desc,
            confidence_score=confidence,
            created_at=utc_now(),
        )
