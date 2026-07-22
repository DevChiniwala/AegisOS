import math
from typing import Dict
from core.schemas.transaction import TransactionCreate
from services.feature_engine.extractors.base import ExtractionContext

class TemporalFeatureExtractor:
    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        features = {}
        tx_time = transaction.timestamp
        
        hour = tx_time.hour
        features['hour_sin'] = math.sin(2 * math.pi * hour / 24)
        features['hour_cos'] = math.cos(2 * math.pi * hour / 24)
        
        day = tx_time.weekday()
        features['day_sin'] = math.sin(2 * math.pi * day / 7)
        features['day_cos'] = math.cos(2 * math.pi * day / 7)
        
        features['is_weekend'] = 1.0 if day >= 5 else 0.0
        features['is_night'] = 1.0 if hour >= 22 or hour < 6 else 0.0
        features['is_business_hours'] = 1.0 if 9 <= hour <= 17 and day < 5 else 0.0
        
        if context.history:
            last_tx_time = max(t.timestamp for t in context.history)
            features['seconds_since_last_transaction'] = (tx_time - last_tx_time).total_seconds()
        else:
            features['seconds_since_last_transaction'] = -1.0
            
        windows = [(60, '1min'), (300, '5min'), (3600, '1hour'), (86400, '24hours'), (604800, '7days'), (2592000, '30days')]
        
        for seconds, name in windows:
            count = 0
            amount_sum = 0.0
            for t in context.history:
                if (tx_time - t.timestamp).total_seconds() <= seconds:
                    count += 1
                    amount_sum += float(t.amount)
            features[f'transactions_last_{name}'] = float(count)
            if name in ['1hour', '24hours', '7days']:
                features[f'amount_last_{name}'] = amount_sum

        if context.user and context.user.created_at:
            features['time_since_account_creation_days'] = (tx_time - context.user.created_at).total_seconds() / 86400.0
        else:
            features['time_since_account_creation_days'] = 0.0
            
        features['is_first_transaction'] = 1.0 if not context.history else 0.0
        
        return features
