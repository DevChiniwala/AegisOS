"""
Behavioral Anomaly Detector.
"""
from typing import Tuple, List
import math
from core.schemas.transaction import TransactionCreate
from services.behavioral_ai.profiles import BehaviorProfile

class BehavioralDeviation:
    def __init__(self, dimension: str, score: float, description: str, severity: str):
        self.dimension = dimension
        self.score = score
        self.description = description
        self.severity = severity

class BehavioralAnomalyDetector:
    def detect_spending_anomaly(self, profile: BehaviorProfile, transaction: TransactionCreate) -> Tuple[float, str]:
        if profile.transaction_count < 5 or profile.spending.std == 0:
            return 0.0, "Insufficient data for spending anomaly detection"
        
        z_score = abs(transaction.amount - profile.spending.mean) / (profile.spending.std + 1e-5)
        score = min(1.0, max(0.0, z_score / 5.0)) # Normalize
        return score, f"Amount {transaction.amount} deviates significantly from mean {profile.spending.mean:.2f}"

    def detect_temporal_anomaly(self, profile: BehaviorProfile, transaction: TransactionCreate) -> Tuple[float, str]:
        hour = transaction.timestamp.hour if hasattr(transaction.timestamp, 'hour') else 0
        if not profile.temporal.typical_hours_histogram:
             return 0.0, "No temporal data"
             
        total = sum(profile.temporal.typical_hours_histogram.values())
        freq = profile.temporal.typical_hours_histogram.get(hour, 0) / total
        
        # If the time is very unusual (< 5% frequency)
        if freq < 0.05:
            return 0.8, f"Unusual transaction time: hour {hour}"
        return 0.0, "Normal time"

    def detect_geo_anomaly(self, profile: BehaviorProfile, transaction: TransactionCreate) -> Tuple[float, str]:
        metadata = getattr(transaction, "metadata", {})
        loc = metadata.get("location")
        if not loc:
            return 0.0, "No location data"
            
        if loc not in profile.geo.known_locations:
            return 0.9, f"Unknown location: {loc}"
        return 0.0, "Known location"

    def detect_device_anomaly(self, profile: BehaviorProfile, transaction: TransactionCreate) -> Tuple[float, str]:
         metadata = getattr(transaction, "metadata", {})
         dev = metadata.get("device_id")
         if not dev:
             return 0.0, "No device data"
         if dev not in profile.device.known_devices:
             return 0.8, f"New device detected: {dev}"
         return 0.0, "Known device"

    def detect_merchant_anomaly(self, profile: BehaviorProfile, transaction: TransactionCreate) -> Tuple[float, str]:
         metadata = getattr(transaction, "metadata", {})
         cat = metadata.get("merchant_category")
         if not cat:
             return 0.0, "No category data"
         if cat not in profile.merchant.known_categories:
             return 0.7, f"Unusual merchant category: {cat}"
         return 0.0, "Known category"

    def aggregate_anomalies(self, scores: List[Tuple[float, str]]) -> float:
        """Weighted combination of anomaly scores."""
        if not scores:
            return 0.0
        
        weights = {
            "spending": 0.3,
            "geo": 0.25,
            "device": 0.2,
            "temporal": 0.15,
            "merchant": 0.1
        }
        
        total_score = 0.0
        weight_sum = 0.0
        
        for score, dim in scores:
            w = weights.get(dim, 0.1)
            total_score += score * w
            weight_sum += w
            
        return total_score / weight_sum if weight_sum > 0 else 0.0
