import math
import hashlib
from typing import Dict
from core.schemas.transaction import TransactionCreate, TransactionType
from services.feature_engine.extractors.base import ExtractionContext


def _stable_encode(value: str) -> float:
    return int(hashlib.md5(value.encode()).hexdigest(), 16) % 10000 / 10000.0

class TransactionFeatureExtractor:
    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        features = {}
        amount = float(transaction.amount)
        
        features['amount_log'] = math.log1p(max(0, amount))
        
        history_amounts = [float(t.amount) for t in context.history]
        if history_amounts:
            mean = sum(history_amounts) / len(history_amounts)
            variance = sum((x - mean) ** 2 for x in history_amounts) / len(history_amounts)
            std = math.sqrt(variance) if variance > 0 else 1.0
            features['amount_zscore'] = (amount - mean) / std
            features['amount_to_avg_ratio'] = amount / mean if mean > 0 else 0.0
            max_amount = max(history_amounts)
            features['amount_to_max_ratio'] = amount / max_amount if max_amount > 0 else 0.0
        else:
            features['amount_zscore'] = 0.0
            features['amount_to_avg_ratio'] = 0.0
            features['amount_to_max_ratio'] = 0.0

        features['is_round_amount'] = 1.0 if amount % 10 == 0 else 0.0
        features['is_large_amount'] = 1.0 if amount > 10000 else 0.0
        
        is_foreign = 1.0
        if context.user and context.user.country and transaction.currency:
            if context.user.country == 'US' and transaction.currency == 'USD':
                is_foreign = 0.0
        features['currency_is_foreign'] = is_foreign

        channel = transaction.channel.value if hasattr(transaction.channel, 'value') else str(transaction.channel)
        features['channel_encoding'] = _stable_encode(channel)

        tx_type = transaction.type.value if hasattr(transaction.type, 'value') else str(transaction.type)
        features['transaction_type_encoding'] = _stable_encode(tx_type)
        
        return features
