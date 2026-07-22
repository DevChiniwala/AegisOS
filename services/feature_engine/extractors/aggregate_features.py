import math
from typing import Dict
from core.schemas.transaction import TransactionCreate
from services.feature_engine.extractors.base import ExtractionContext

class AggregateFeatureExtractor:
    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        features = {}
        amount = float(transaction.amount)
        
        windows = [60, 300, 3600, 86400, 604800, 2592000]
        window_names = ['1m', '5m', '1h', '24h', '7d', '30d']
        
        for w, name in zip(windows, window_names):
            w_amounts = [float(t.amount) for t in context.history if (context.timestamp - t.timestamp).total_seconds() <= w]
            features[f'count_{name}'] = float(len(w_amounts))
            
            if w_amounts:
                features[f'sum_{name}'] = sum(w_amounts)
                mean = sum(w_amounts) / len(w_amounts)
                features[f'mean_{name}'] = mean
                features[f'min_{name}'] = min(w_amounts)
                features[f'max_{name}'] = max(w_amounts)
                variance = sum((x - mean)**2 for x in w_amounts) / len(w_amounts)
                features[f'std_{name}'] = math.sqrt(variance)
            else:
                features[f'sum_{name}'] = 0.0
                features[f'mean_{name}'] = 0.0
                features[f'min_{name}'] = 0.0
                features[f'max_{name}'] = 0.0
                features[f'std_{name}'] = 0.0

        mean_24h = features.get('mean_24h', 0.0)
        features['amount_to_avg_amount_24h_ratio'] = amount / mean_24h if mean_24h > 0 else 0.0
        
        count_24h = features.get('count_24h', 0.0)
        count_7d = features.get('count_7d', 0.0)
        avg_count_24h_over_7d = count_7d / 7.0 if count_7d > 0 else 0.0
        features['tx_count_acceleration'] = count_24h / avg_count_24h_over_7d if avg_count_24h_over_7d > 0 else 0.0
        
        return features
