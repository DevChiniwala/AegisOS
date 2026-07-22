"""
Money Mule scenario generator.
"""
from typing import List
from core.schemas.transaction import TransactionCreate, TransactionType
from core.utils.helpers import utc_now

def generate_money_mule_scenario(mule_id: str, target_account_id: str) -> List[TransactionCreate]:
    txs = []
    # Rapid receive
    txs.append(TransactionCreate(
        type=TransactionType.TRANSFER,
        amount=2000.00,
        currency="USD",
        timestamp=utc_now(),
        metadata={
            "user_id": mule_id,
            "is_fraud": True,
            "scenario": "money_mule_receive"
        }
    ))
    # Forward pattern
    txs.append(TransactionCreate(
        type=TransactionType.TRANSFER,
        amount=1950.00,
        currency="USD",
        timestamp=utc_now(),
        metadata={
            "user_id": mule_id,
            "target_id": target_account_id,
            "is_fraud": True,
            "scenario": "money_mule_forward"
        }
    ))
    return txs
