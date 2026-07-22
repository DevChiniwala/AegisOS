"""
Synthetic Identity scenario generator.
"""
from typing import List
from core.schemas.transaction import TransactionCreate, TransactionType
from core.utils.helpers import utc_now

def generate_synthetic_identity_scenario(new_user_id: str) -> List[TransactionCreate]:
    txs = []
    # Rapid credit building followed by bust-out
    for amount in [50, 100, 500, 1000]: # Normal looking build up
        txs.append(TransactionCreate(
            type=TransactionType.PURCHASE,
            amount=float(amount),
            currency="USD",
            timestamp=utc_now(),
            metadata={"user_id": new_user_id, "is_fraud": False}
        ))
        
    # Bust out pattern
    for _ in range(5):
        txs.append(TransactionCreate(
            type=TransactionType.PURCHASE,
            amount=5000.0,
            currency="USD",
            timestamp=utc_now(),
            metadata={"user_id": new_user_id, "is_fraud": True, "scenario": "synthetic_identity_bust_out"}
        ))
    return txs
