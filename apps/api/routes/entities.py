"""
Entity routes.
"""
from fastapi import APIRouter, Depends
from core.schemas.entity import UserProfile, MerchantProfile, DeviceFingerprint

router = APIRouter()

@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    return UserProfile(id=user_id, created_at="2023-01-01T00:00:00Z", updated_at="2023-01-01T00:00:00Z", risk_score=0.1)

@router.get("/merchants/{merchant_id}", response_model=MerchantProfile)
async def get_merchant(merchant_id: str):
    return MerchantProfile(id=merchant_id, created_at="2023-01-01T00:00:00Z", updated_at="2023-01-01T00:00:00Z", category="retail")

@router.get("/devices/{device_id}", response_model=DeviceFingerprint)
async def get_device(device_id: str):
    return DeviceFingerprint(id=device_id, ip_address="127.0.0.1", user_agent="Mozilla")

@router.get("/users/{user_id}/transactions")
async def get_user_transactions(user_id: str):
    return []

@router.get("/users/{user_id}/risk-profile")
async def get_user_risk_profile(user_id: str):
    return {"user_id": user_id, "risk_score": 0.1, "factors": []}
