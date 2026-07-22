from ..base import BaseAgent, InvestigationContext
from core.schemas.investigation import Finding
from core.utils.helpers import utc_now
import uuid

class GraphDetective(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GraphDetective",
            role="Network Analyst",
            description="Queries graph engine for entity connections and fraud ring proximity"
        )

    async def investigate(self, context: InvestigationContext) -> Finding:
        graph_data = context.graph_data
        findings_parts = []
        confidence = 0.5

        neighbors = graph_data.get('neighbors', [])
        if neighbors:
            findings_parts.append(f"Entity connected to {len(neighbors)} nodes in the graph")
            high_risk_neighbors = [n for n in neighbors if n.get('risk_score', 0) > 0.7]
            if high_risk_neighbors:
                findings_parts.append(f"{len(high_risk_neighbors)} high-risk connections detected")
                confidence += 0.2
        else:
            findings_parts.append("Entity is isolated with no graph connections")

        fraud_rings = graph_data.get('fraud_rings', [])
        if fraud_rings:
            findings_parts.append(f"Entity appears in {len(fraud_rings)} potential fraud ring(s)")
            confidence += 0.25
        else:
            findings_parts.append("No fraud ring association found")

        shared = graph_data.get('shared_entities', {})
        shared_nodes = shared.get('shared_nodes', [])
        if shared_nodes:
            findings_parts.append(f"Shares {len(shared_nodes)} entities with counterparty")
            confidence += 0.1

        centrality = graph_data.get('centrality', 0.0)
        if centrality > 0.5:
            findings_parts.append(f"High graph centrality ({centrality:.2f}) — potential hub entity")
            confidence += 0.1

        confidence = min(confidence, 0.99)

        return Finding(
            finding_id=str(uuid.uuid4()),
            agent_name=self.name,
            title="Network Topology Analysis",
            description="; ".join(findings_parts),
            confidence_score=confidence,
            created_at=utc_now()
        )
