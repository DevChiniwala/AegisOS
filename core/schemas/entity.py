from datetime import datetime, date
from typing import Optional
from pydantic import Field
from .base import BaseSchema


class UserProfile(BaseSchema):
    user_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    kyc_status: str
    kyc_verified_at: Optional[datetime] = None
    risk_tier: str
    account_age_days: int
    country: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MerchantProfile(BaseSchema):
    merchant_id: str
    name: str
    category: str
    mcc_code: str
    risk_tier: str
    country: str
    registration_date: datetime
    is_verified: bool


class DeviceFingerprint(BaseSchema):
    device_id: str
    user_id: str
    device_type: str
    os: str
    browser: Optional[str] = None
    screen_resolution: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    is_emulator: bool = False
    is_rooted: bool = False
    first_seen: datetime
    last_seen: datetime


class AccountInfo(BaseSchema):
    account_id: str
    user_id: str
    account_type: str
    bank_code: str
    balance: float
    currency: str
    status: str
    opened_at: datetime
