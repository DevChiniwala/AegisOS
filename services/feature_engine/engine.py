import time
from typing import Optional, List, Dict
from core.schemas.transaction import TransactionCreate
from core.schemas.entity import UserProfile, MerchantProfile, DeviceFingerprint
from core.utils.logging import get_logger
from services.feature_engine.extractors.base import ExtractionContext
from services.feature_engine.extractors.transaction_features import TransactionFeatureExtractor
from services.feature_engine.extractors.temporal_features import TemporalFeatureExtractor
from services.feature_engine.extractors.geo_features import GeoFeatureExtractor
from services.feature_engine.extractors.device_features import DeviceFeatureExtractor
from services.feature_engine.extractors.behavioral_features import BehavioralFeatureExtractor
from services.feature_engine.extractors.graph_features import GraphFeatureExtractor
from services.feature_engine.extractors.aggregate_features import AggregateFeatureExtractor
from core.utils.helpers import utc_now, Timer

logger = get_logger(__name__)

class FeatureEngineeringEngine:
    def __init__(self):
        self.extractors = [
            TransactionFeatureExtractor(),
            TemporalFeatureExtractor(),
            GeoFeatureExtractor(),
            DeviceFeatureExtractor(),
            BehavioralFeatureExtractor(),
            GraphFeatureExtractor(),
            AggregateFeatureExtractor()
        ]

    def extract_features(
        self,
        transaction: TransactionCreate,
        user: Optional[UserProfile],
        merchant: Optional[MerchantProfile],
        device: Optional[DeviceFingerprint],
        history: List[TransactionCreate]
    ) -> Dict[str, float]:
        features: Dict[str, float] = {}
        context = ExtractionContext(
            user=user,
            merchant=merchant,
            device=device,
            history=history,
            timestamp=utc_now()
        )
        
        with Timer() as timer:
            for extractor in self.extractors:
                try:
                    ext_features = extractor.extract(transaction, context)
                    features.update(ext_features)
                except Exception as e:
                    logger.error("Feature extraction failed", extractor=extractor.__class__.__name__, error=str(e))
        
        logger.debug("Feature extraction complete", latency_ms=timer.elapsed_ms)
        return features
