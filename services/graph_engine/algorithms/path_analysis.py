import networkx as nx
from typing import List, Dict

class PathAnalyzer:
    def shortest_path(self, graph: nx.Graph, source: str, target: str) -> List[str]:
        try:
            return nx.shortest_path(graph, source, target)
        except nx.NetworkXNoPath:
            return []
        except nx.NodeNotFound:
            return []

    def all_paths(self, graph: nx.Graph, source: str, target: str, max_depth: int = 5) -> List[List[str]]:
        try:
            return list(nx.all_simple_paths(graph, source, target, cutoff=max_depth))
        except nx.NodeNotFound:
            return []

    def money_flow_trace(self, graph: nx.DiGraph, source: str, max_depth: int = 10) -> Dict:
        # Traverse out-edges from source to build a tree
        if source not in graph:
            return {}
        
        edges = list(nx.bfs_edges(graph, source, depth_limit=max_depth))
        return {"source": source, "edges": edges}

    def circular_flow_detection(self, graph: nx.DiGraph, entity_id: str) -> List[List[str]]:
        # Detect circular money flows involving entity_id
        if entity_id not in graph:
            return []
            
        cycles = list(nx.simple_cycles(graph))
        return [cycle for cycle in cycles if entity_id in cycle]
