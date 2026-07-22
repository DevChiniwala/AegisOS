import time
from typing import Dict, List, Optional
from datetime import datetime

class FeatureStore:
    def __init__(self):
        self._store = {}
        
    def store_features(self, entity_id: str, features: Dict[str, float], timestamp: datetime):
        if entity_id not in self._store:
            self._store[entity_id] = []
        self._store[entity_id].append({
            'timestamp': timestamp,
            'features': features
        })
        
    def get_features(self, entity_id: str) -> Optional[Dict[str, float]]:
        records = self._store.get(entity_id, [])
        if not records:
            return None
        return records[-1]['features']
        
    def get_feature_history(self, entity_id: str, window_seconds: float) -> List[Dict]:
        records = self._store.get(entity_id, [])
        if not records:
            return []
        now = datetime.utcnow()
        return [r for r in records if (now - r['timestamp']).total_seconds() <= window_seconds]
