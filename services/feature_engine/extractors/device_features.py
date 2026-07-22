from typing import Dict
from core.schemas.transaction import TransactionCreate
from services.feature_engine.extractors.base import ExtractionContext

class DeviceFeatureExtractor:
    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        features = {}
        
        if context.device:
            features['is_new_device'] = 0.0 if context.device.last_seen_at else 1.0
            if context.device.created_at:
                features['device_age_days'] = (context.timestamp - context.device.created_at).total_seconds() / 86400.0
            else:
                features['device_age_days'] = 0.0
                
            features['device_user_count'] = float(getattr(context.device, 'user_count', 1))
            features['is_emulator'] = 1.0 if getattr(context.device, 'is_emulator', False) else 0.0
            features['is_rooted'] = 1.0 if getattr(context.device, 'is_rooted', False) else 0.0
            
            device_type = getattr(context.device, 'device_type', '')
            features['device_type_encoding'] = hash(device_type) % 100 / 100.0
            
            os = getattr(context.device, 'os', '')
            features['os_encoding'] = hash(os) % 100 / 100.0
            
        else:
            features['is_new_device'] = 1.0
            features['device_age_days'] = -1.0
            features['device_user_count'] = 1.0
            features['is_emulator'] = 0.0
            features['is_rooted'] = 0.0
            features['device_type_encoding'] = 0.0
            features['os_encoding'] = 0.0
            
        device_changes = 0
        last_device = None
        for t in context.history:
            if (context.timestamp - t.timestamp).total_seconds() <= 7 * 86400:
                cur_device = getattr(t, 'device_id', None)
                if cur_device and cur_device != last_device:
                    device_changes += 1
                    last_device = cur_device
        features['device_change_frequency_7d'] = float(device_changes)
        
        return features
