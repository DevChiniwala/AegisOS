"""
Behavioral Intelligence Engine.
"""
from typing import Dict, List, Optional
from core.schemas.transaction import TransactionCreate
from core.utils.logging import get_logger
from services.behavioral_ai.profiles import BehaviorProfile, SpendingProfile, TemporalProfile, GeoProfile, DeviceProfile, MerchantBehaviorProfile
from services.behavioral_ai.anomaly import BehavioralAnomalyDetector, BehavioralDeviation
from core.utils.helpers import utc_now

logger = get_logger(__name__)

class BehavioralIntelligenceEngine:
    """
    Engine to manage behavioral profiles and detect anomalies based on transaction behavior.
    """
    def __init__(self):
        self.profiles: Dict[str, BehaviorProfile] = {}
        self.detector = BehavioralAnomalyDetector()

    def _get_or_create_profile(self, user_id: str) -> BehaviorProfile:
        if user_id not in self.profiles:
            self.profiles[user_id] = BehaviorProfile(
                user_id=user_id,
                transaction_count=0,
                last_updated=utc_now(),
                spending=SpendingProfile(),
                temporal=TemporalProfile(),
                geo=GeoProfile(),
                device=DeviceProfile(),
                merchant=MerchantBehaviorProfile()
            )
        return self.profiles[user_id]

    def update_profile(self, user_id: str, transaction: TransactionCreate) -> None:
        """Update the behavioral profile for a user given a new transaction."""
        profile = self._get_or_create_profile(user_id)
        
        # Update metrics
        profile.transaction_count += 1
        profile.last_updated = utc_now()
        profile.spending.update(transaction.amount, transaction.timestamp.weekday() if hasattr(transaction.timestamp, 'weekday') else 0)
        
        # Extract features for updating
        hour = transaction.timestamp.hour if hasattr(transaction.timestamp, 'hour') else 0
        day = transaction.timestamp.weekday() if hasattr(transaction.timestamp, 'weekday') else 0
        profile.temporal.update(hour, day)
        
        # We assume transaction has location, device, merchant fields or metadata
        metadata = getattr(transaction, "metadata", {})
        if metadata:
            if "location" in metadata:
                profile.geo.update(metadata["location"])
            if "device_id" in metadata:
                profile.device.update(metadata["device_id"])
            if "merchant_category" in metadata:
                profile.merchant.update(getattr(transaction, "merchant_id", "unknown"), metadata["merchant_category"])

    def get_anomaly_score(self, user_id: str, transaction: TransactionCreate) -> float:
        """Calculate the overall behavioral anomaly score for a transaction."""
        deviations = self.get_deviations(user_id, transaction)
        if not deviations:
            return 0.0
        scores = [(d.score, d.dimension) for d in deviations]
        return self.detector.aggregate_anomalies(scores)

    def get_deviations(self, user_id: str, transaction: TransactionCreate) -> List[BehavioralDeviation]:
        """Get specific behavioral deviations for a transaction."""
        if user_id not in self.profiles:
            return []
        
        profile = self.profiles[user_id]
        deviations = []
        
        # Detect anomalies across dimensions
        spending_score, desc = self.detector.detect_spending_anomaly(profile, transaction)
        if spending_score > 0.5:
            deviations.append(BehavioralDeviation("spending", spending_score, desc, "high" if spending_score > 0.8 else "medium"))
            
        temporal_score, desc = self.detector.detect_temporal_anomaly(profile, transaction)
        if temporal_score > 0.5:
            deviations.append(BehavioralDeviation("temporal", temporal_score, desc, "high" if temporal_score > 0.8 else "medium"))
            
        geo_score, desc = self.detector.detect_geo_anomaly(profile, transaction)
        if geo_score > 0.5:
             deviations.append(BehavioralDeviation("geo", geo_score, desc, "high" if geo_score > 0.8 else "medium"))
             
        device_score, desc = self.detector.detect_device_anomaly(profile, transaction)
        if device_score > 0.5:
            deviations.append(BehavioralDeviation("device", device_score, desc, "high" if device_score > 0.8 else "medium"))
            
        merchant_score, desc = self.detector.detect_merchant_anomaly(profile, transaction)
        if merchant_score > 0.5:
            deviations.append(BehavioralDeviation("merchant", merchant_score, desc, "high" if merchant_score > 0.8 else "medium"))
            
        return deviations
