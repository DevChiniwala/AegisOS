from typing import Dict
from core.schemas.transaction import TransactionCreate
from services.feature_engine.extractors.base import ExtractionContext

class GraphFeatureExtractor:
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
        return features
