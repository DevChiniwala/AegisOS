"""
Card fraud scenario generator.
"""
from core.schemas.transaction import TransactionCreate, TransactionType
from core.utils.helpers import utc_now

def generate_card_fraud_scenario(user_id: str, merchant_id: str) -> TransactionCreate:
    return TransactionCreate(
        type=TransactionType.PURCHASE,
        amount=1500.00,
        currency="USD",
        timestamp=utc_now(),
        metadata={
            "user_id": user_id,
            "merchant_id": merchant_id,
            "is_fraud": True,
            "scenario": "card_fraud",
            "merchant_category": "electronics",
            "location": "RU" # Unusual location
        }
    )
