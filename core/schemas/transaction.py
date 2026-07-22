from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import Field
from uuid import UUID
from .base import BaseSchema


class TransactionType(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    UPI = "UPI"
    WIRE_TRANSFER = "WIRE_TRANSFER"
    ACH = "ACH"
    CRYPTO = "CRYPTO"
    P2P = "P2P"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    FLAGGED = "FLAGGED"
    BLOCKED = "BLOCKED"
    UNDER_REVIEW = "UNDER_REVIEW"


class TransactionCreate(BaseSchema):
    transaction_id: str
    type: TransactionType
    amount: float
    currency: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_id: str
    receiver_id: str
    sender_account: str
    receiver_account: str
    merchant_id: Optional[str] = None
    channel: str
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    country_code: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransactionResponse(TransactionCreate):
    risk_score: Optional[float] = None
    risk_verdict: Optional[str] = None
    processing_time_ms: Optional[int] = None


class TransactionBatch(BaseSchema):
    transactions: List[TransactionCreate]
