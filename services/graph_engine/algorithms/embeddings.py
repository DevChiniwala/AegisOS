import networkx as nx
import numpy as np
from typing import Dict, List, Tuple
try:
    from node2vec import Node2Vec
except ImportError:
    Node2Vec = None

class NodeEmbedder:
    def node2vec_embed(self, graph: nx.Graph, dimensions: int = 64, walk_length: int = 30, num_walks: int = 200) -> Dict[str, List[float]]:
        if Node2Vec is None:
            raise ImportError("node2vec is not installed. Install with: pip install node2vec")
            
        node2vec = Node2Vec(graph, dimensions=dimensions, walk_length=walk_length, num_walks=num_walks, workers=1)
        model = node2vec.fit(window=10, min_count=1, batch_words=4)
        
        embeddings = {}
        for node in graph.nodes():
            embeddings[str(node)] = model.wv[str(node)].tolist()
            
        return embeddings

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def find_similar_nodes(self, embeddings: Dict[str, List[float]], entity_id: str, top_k: int = 10) -> List[Tuple[str, float]]:
        if entity_id not in embeddings:
            return []
            
        target_emb = embeddings[entity_id]
        similarities = []
        
        for node, emb in embeddings.items():
            if node != entity_id:
                sim = self.similarity(target_emb, emb)
                similarities.append((node, sim))
                
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
