from typing import Protocol, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from core.schemas.transaction import TransactionCreate
from core.schemas.entity import UserProfile, MerchantProfile, DeviceFingerprint

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
