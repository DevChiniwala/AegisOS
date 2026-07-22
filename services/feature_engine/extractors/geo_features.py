import math
from typing import Dict
from core.schemas.transaction import TransactionCreate
from services.feature_engine.extractors.base import ExtractionContext

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class GeoFeatureExtractor:
    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        features = {}
        
        lat = getattr(transaction.location, 'latitude', 0.0) if transaction.location else 0.0
        lon = getattr(transaction.location, 'longitude', 0.0) if transaction.location else 0.0
        
        features['geo_lat_normalized'] = lat / 90.0
        features['geo_lon_normalized'] = lon / 180.0
        
        features['geo_distance_from_last_transaction'] = -1.0
        features['geo_velocity_kmh'] = -1.0
        features['is_impossible_travel'] = 0.0
        
        if context.history and transaction.location:
            last_tx = max(context.history, key=lambda t: t.timestamp)
            last_lat = getattr(last_tx.location, 'latitude', None)
            last_lon = getattr(last_tx.location, 'longitude', None)
            
            if last_lat is not None and last_lon is not None:
                dist = haversine(lat, lon, last_lat, last_lon)
                features['geo_distance_from_last_transaction'] = dist
                
                time_delta = max(1.0, (transaction.timestamp - last_tx.timestamp).total_seconds()) / 3600.0
                velocity = dist / time_delta
                features['geo_velocity_kmh'] = velocity
                features['is_impossible_travel'] = 1.0 if velocity > 900.0 else 0.0
                
        tx_country = getattr(transaction.location, 'country', '') if transaction.location else ''
        user_country = context.user.country if context.user else ''
        features['is_domestic'] = 1.0 if tx_country == user_country and tx_country != '' else 0.0
        features['country_risk_score'] = 0.5
        
        countries_24h = set()
        cities_24h = set()
        for t in context.history:
            if (transaction.timestamp - t.timestamp).total_seconds() <= 86400:
                if t.location:
                    c = getattr(t.location, 'country', '')
                    if c: countries_24h.add(c)
                    city = getattr(t.location, 'city', '')
                    if city: cities_24h.add(city)
        if tx_country: countries_24h.add(tx_country)
        
        features['unique_countries_24h'] = float(len(countries_24h))
        features['unique_cities_24h'] = float(len(cities_24h))
        
        return features
