"""
GraphRAG — Hierarchical community summarization over the knowledge graph.

Combines local (entity-specific) and global (community-level) retrieval
for comprehensive fraud context.
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from core.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Community:
    community_id: str
    level: int
    members: List[str] = field(default_factory=list)
    summary: str = ""
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    content: str
    source_type: str
    relevance_score: float
    entity_id: Optional[str] = None
    community_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GraphRAGEngine:
    """Hierarchical community-based retrieval over the fraud knowledge graph."""

    def __init__(self):
        self._communities: Dict[str, Community] = {}
        self._entity_index: Dict[str, List[str]] = {}
        self._summaries: List[Dict[str, Any]] = []

    def build_communities(self, graph_data: Dict[str, Any]) -> List[Community]:
        """Detect communities and generate hierarchical summaries."""
        try:
            import networkx as nx
            from community import community_louvain
        except ImportError:
            logger.warning("networkx or community not available for GraphRAG")
            return []

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        if not nodes or not edges:
            return []

        G = nx.Graph()
        for node in nodes:
            G.add_node(node.get("id", ""), **node)
        for edge in edges:
            G.add_edge(edge.get("source", ""), edge.get("target", ""), **edge)

        partition = community_louvain.best_partition(G)

        community_members: Dict[int, List[str]] = {}
        for node_id, comm_id in partition.items():
            community_members.setdefault(comm_id, []).append(node_id)

        communities = []
        for comm_id, members in community_members.items():
            risk_scores = []
            for m in members:
                node_data = G.nodes.get(m, {})
                if "risk_score" in node_data:
                    risk_scores.append(node_data["risk_score"])

            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

            community = Community(
                community_id=f"comm_{comm_id}",
                level=0,
                members=members,
                summary=self._summarize_community(G, members),
                risk_score=avg_risk,
                metadata={"size": len(members), "density": self._community_density(G, members)},
            )
            communities.append(community)
            self._communities[community.community_id] = community

            for member in members:
                self._entity_index.setdefault(member, []).append(community.community_id)

        return communities

    def query_local(self, entity_id: str, top_k: int = 5) -> List[RetrievalResult]:
        """Retrieve entity-specific context (local search)."""
        results = []

        community_ids = self._entity_index.get(entity_id, [])
        for comm_id in community_ids[:top_k]:
            community = self._communities.get(comm_id)
            if community:
                results.append(RetrievalResult(
                    content=community.summary,
                    source_type="community",
                    relevance_score=1.0 - (0.1 * len(results)),
                    entity_id=entity_id,
                    community_id=comm_id,
                    metadata={"members": len(community.members), "risk": community.risk_score},
                ))

        return results

    def query_global(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """Retrieve thematic context across all communities (global search)."""
        results = []
        query_lower = query.lower()

        scored = []
        for comm_id, community in self._communities.items():
            score = self._text_relevance(query_lower, community.summary.lower())
            if score > 0:
                scored.append((score, community))

        scored.sort(key=lambda x: x[0], reverse=True)

        for score, community in scored[:top_k]:
            results.append(RetrievalResult(
                content=community.summary,
                source_type="global_community",
                relevance_score=score,
                community_id=community.community_id,
                metadata={"level": community.level, "risk": community.risk_score},
            ))

        return results

    def query(self, entity_id: Optional[str] = None, query: Optional[str] = None, top_k: int = 5) -> List[RetrievalResult]:
        """Combined local + global retrieval."""
        results = []
        if entity_id:
            results.extend(self.query_local(entity_id, top_k=top_k // 2))
        if query:
            results.extend(self.query_global(query, top_k=top_k // 2))

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:top_k]

    def _summarize_community(self, G, members: List[str]) -> str:
        """Generate a summary description of a community."""
        subgraph = G.subgraph(members)
        num_edges = subgraph.number_of_edges()
        node_types = set()
        for m in members:
            node_type = G.nodes[m].get("type", "entity")
            node_types.add(node_type)

        return (
            f"Community of {len(members)} entities ({', '.join(node_types)}) "
            f"with {num_edges} internal connections. "
            f"Density: {self._community_density(G, members):.3f}."
        )

    @staticmethod
    def _community_density(G, members: List[str]) -> float:
        if len(members) < 2:
            return 0.0
        subgraph = G.subgraph(members)
        max_edges = len(members) * (len(members) - 1) / 2
        return subgraph.number_of_edges() / max_edges if max_edges > 0 else 0.0

    @staticmethod
    def _text_relevance(query: str, text: str) -> float:
        query_terms = set(query.split())
        text_terms = set(text.split())
        if not query_terms:
            return 0.0
        overlap = query_terms & text_terms
        return len(overlap) / len(query_terms)
