"""
Account Takeover scenario generator.
"""
from typing import List
from core.schemas.transaction import TransactionCreate, TransactionType
from core.utils.helpers import utc_now

def generate_ato_scenario(user_id: str, new_device_id: str) -> List[TransactionCreate]:
    return [
        TransactionCreate(
            type=TransactionType.TRANSFER,
            amount=5000.00,
            currency="USD",
            timestamp=utc_now(),
            metadata={
                "user_id": user_id,
                "device_id": new_device_id,
                "is_fraud": True,
                "scenario": "account_takeover",
                "notes": "Transfer immediately after login from new device"
            }
        )
    ]
