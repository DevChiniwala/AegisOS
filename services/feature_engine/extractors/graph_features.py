import logging
import networkx as nx
from typing import Dict, Optional
from core.schemas.transaction import TransactionCreate
from services.feature_engine.extractors.base import ExtractionContext

logger = logging.getLogger(__name__)


class GraphFeatureExtractor:
    def __init__(self, graph: Optional[nx.Graph] = None):
        self._graph = graph

    def set_graph(self, graph: nx.Graph):
        self._graph = graph

    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        features = {
            'sender_degree_centrality': 0.0,
            'receiver_degree_centrality': 0.0,
            'sender_pagerank': 0.0,
            'receiver_pagerank': 0.0,
            'sender_community_id': 0.0,
            'receiver_community_id': 0.0,
            'shared_device_count': 0.0,
            'shared_ip_count': 0.0,
            'sender_risk_propagation_score': 0.0,
            'graph_distance_sender_receiver': -1.0
        }

        if self._graph is None or self._graph.number_of_nodes() == 0:
            return features

        sender_id = transaction.user_id
        receiver_id = transaction.merchant_id

        try:
            if sender_id and sender_id in self._graph:
                degree = self._graph.degree(sender_id)
                total = self._graph.number_of_nodes() - 1
                features['sender_degree_centrality'] = degree / total if total > 0 else 0.0

            if receiver_id and receiver_id in self._graph:
                degree = self._graph.degree(receiver_id)
                total = self._graph.number_of_nodes() - 1
                features['receiver_degree_centrality'] = degree / total if total > 0 else 0.0

            if sender_id and sender_id in self._graph:
                pagerank = nx.pagerank(self._graph)
                features['sender_pagerank'] = pagerank.get(sender_id, 0.0)
                if receiver_id:
                    features['receiver_pagerank'] = pagerank.get(receiver_id, 0.0)

            if sender_id and receiver_id and sender_id in self._graph and receiver_id in self._graph:
                try:
                    path = nx.shortest_path_length(self._graph, sender_id, receiver_id)
                    features['graph_distance_sender_receiver'] = float(path)
                except nx.NetworkXNoPath:
                    features['graph_distance_sender_receiver'] = -1.0

                sender_neighbors = set(self._graph.neighbors(sender_id))
                receiver_neighbors = set(self._graph.neighbors(receiver_id))
                shared = sender_neighbors & receiver_neighbors
                devices = [n for n in shared if self._graph.nodes[n].get('node_type') == 'DEVICE']
                ips = [n for n in shared if self._graph.nodes[n].get('node_type') == 'IP_ADDRESS']
                features['shared_device_count'] = float(len(devices))
                features['shared_ip_count'] = float(len(ips))

        except Exception as e:
            logger.warning(f"Graph feature extraction failed: {e}")

        return features
