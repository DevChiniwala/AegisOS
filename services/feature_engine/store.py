from typing import Dict, List, Optional
from datetime import datetime, timezone


class FeatureStore:
    def __init__(self):
        self._store = {}

    def _ensure_aware(self, ts: datetime) -> datetime:
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts

    def store_features(self, entity_id: str, features: Dict[str, float], timestamp: datetime):
        if entity_id not in self._store:
            self._store[entity_id] = []
        self._store[entity_id].append({
            'timestamp': self._ensure_aware(timestamp),
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
        now = datetime.now(timezone.utc)
        return [r for r in records if (now - self._ensure_aware(r['timestamp'])).total_seconds() <= window_seconds]
