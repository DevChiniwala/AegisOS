from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Protocol

from core.schemas.entity import DeviceFingerprint, MerchantProfile, UserProfile
from core.schemas.transaction import TransactionCreate


@dataclass
class ExtractionContext:
    user: Optional[UserProfile]
    merchant: Optional[MerchantProfile]
    device: Optional[DeviceFingerprint]
    history: List[TransactionCreate]
    timestamp: datetime

class FeatureExtractor(Protocol):
    def extract(self, transaction: TransactionCreate, context: ExtractionContext) -> Dict[str, float]:
        ...
