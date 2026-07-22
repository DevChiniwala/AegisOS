import networkx as nx
import community as community_louvain
from typing import List, Set

class CommunityDetector:
    def detect_communities(self, graph: nx.Graph, method: str = 'louvain') -> List[Set[str]]:
        if not graph.nodes():
            return []
            
        if method == 'louvain':
            # Louvain requires undirected graph
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph
            partition = community_louvain.best_partition(undirected_graph)
            
            communities = {}
            for node, comm_id in partition.items():
                if comm_id not in communities:
                    communities[comm_id] = set()
                communities[comm_id].add(node)
            return list(communities.values())
        else:
            # Fallback to label propagation
            undirected_graph = graph.to_undirected() if graph.is_directed() else graph
            c = nx.community.label_propagation_communities(undirected_graph)
            return [set(comm) for comm in c]

    def score_community_risk(self, community: Set[str], graph: nx.Graph) -> float:
        risks = [graph.nodes[n].get('risk_score', 0.0) for n in community if n in graph]
        return sum(risks) / len(risks) if risks else 0.0

    def find_suspicious_communities(self, graph: nx.Graph, min_risk: float = 0.6, min_size: int = 3) -> List[Set[str]]:
        communities = self.detect_communities(graph)
        suspicious = []
        for comm in communities:
            if len(comm) >= min_size:
                risk = self.score_community_risk(comm, graph)
                if risk >= min_risk:
                    suspicious.append(comm)
        return suspicious
