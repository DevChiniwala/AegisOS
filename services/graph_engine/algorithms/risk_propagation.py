import networkx as nx
from typing import Dict, List

class RiskPropagator:
    def propagate(self, graph: nx.Graph, seed_nodes: Dict[str, float], iterations: int = 10, decay: float = 0.85) -> Dict[str, float]:
        """
        Implements a simple belief propagation / label propagation for risk scores.
        Decay factor reduces risk as distance from seed increases.
        """
        scores = {node: 0.0 for node in graph.nodes()}
        for seed, score in seed_nodes.items():
            if seed in scores:
                scores[seed] = score
        
        for _ in range(iterations):
            new_scores = scores.copy()
            for node in graph.nodes():
                if node in seed_nodes:
                    continue  # Keep seed nodes constant
                
                neighbor_scores = [scores[neighbor] for neighbor in graph.neighbors(node)]
                if neighbor_scores:
                    # Risk is max of current risk or max neighbor risk * decay
                    propagated = max(neighbor_scores) * decay
                    new_scores[node] = max(scores[node], propagated)
            
            # Convergence check
            diff = sum(abs(new_scores[n] - scores[n]) for n in graph.nodes())
            scores = new_scores
            if diff < 1e-4:
                break
                
        return scores
