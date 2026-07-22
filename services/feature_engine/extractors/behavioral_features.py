import math
from typing import Dict
from core.schemas.transaction import TransactionCreate
from services.feature_engine.extractors.base import ExtractionContext

class BehavioralFeatureExtractor:
    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        features = {}
        
        amount = float(transaction.amount)
        history_amounts = [float(t.amount) for t in context.history]
        
        if history_amounts:
            mean = sum(history_amounts) / len(history_amounts)
            var = sum((x - mean)**2 for x in history_amounts) / len(history_amounts)
            std = math.sqrt(var) if var > 0 else 1.0
            features['spending_deviation_score'] = abs(amount - mean) / std
            
            sorted_amounts = sorted(history_amounts)
            rank = sum(1 for x in sorted_amounts if x < amount)
            features['amount_percentile'] = rank / len(history_amounts)
        else:
            features['spending_deviation_score'] = 0.0
            features['amount_percentile'] = 1.0
            
        tx_mcc = getattr(context.merchant, 'category_code', '') if context.merchant else ''
        if tx_mcc:
            has_mcc_before = any(getattr(t, 'merchant_category_code', '') == tx_mcc for t in context.history)
            features['merchant_category_novelty'] = 0.0 if has_mcc_before else 1.0
        else:
            features['merchant_category_novelty'] = 1.0
            
        if context.history:
            mean_hour = sum(t.timestamp.hour for t in context.history) / len(context.history)
            features['time_pattern_deviation'] = min(abs(transaction.timestamp.hour - mean_hour), 
                                                     24 - abs(transaction.timestamp.hour - mean_hour)) / 12.0
        else:
            features['time_pattern_deviation'] = 0.0
            
        tx_merchant = transaction.merchant_id
        if tx_merchant:
            merchant_freq = sum(1 for t in context.history if t.merchant_id == tx_merchant)
            features['merchant_frequency'] = float(merchant_freq)
        else:
            features['merchant_frequency'] = 0.0
            
        channel = transaction.channel
        channel_freq = sum(1 for t in context.history if t.channel == channel)
        features['channel_deviation'] = 1.0 if channel_freq == 0 and context.history else 0.0
        
        return features
