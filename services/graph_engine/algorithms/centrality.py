import networkx as nx
from typing import Dict, List, Tuple

class CentralityAnalyzer:
    def degree_centrality(self, graph: nx.Graph, entity_id: str) -> float:
        if entity_id not in graph: return 0.0
        dc = nx.degree_centrality(graph)
        return dc.get(entity_id, 0.0)

    def betweenness_centrality(self, graph: nx.Graph, entity_id: str) -> float:
        if entity_id not in graph: return 0.0
        bc = nx.betweenness_centrality(graph)
        return bc.get(entity_id, 0.0)

    def pagerank(self, graph: nx.Graph, entity_id: str) -> float:
        if entity_id not in graph: return 0.0
        pr = nx.pagerank(graph)
        return pr.get(entity_id, 0.0)

    def compute_all(self, graph: nx.Graph) -> Dict[str, Dict[str, float]]:
        dc = nx.degree_centrality(graph)
        bc = nx.betweenness_centrality(graph)
        pr = nx.pagerank(graph)
        
        results = {}
        for node in graph.nodes():
            results[node] = {
                'degree': dc.get(node, 0.0),
                'betweenness': bc.get(node, 0.0),
                'pagerank': pr.get(node, 0.0)
            }
        return results

    def identify_key_players(self, graph: nx.Graph, top_k: int = 10) -> List[Tuple[str, float]]:
        pr = nx.pagerank(graph)
        sorted_nodes = sorted(pr.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_k]
