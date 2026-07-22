"""
Synthetic Data Generator.
"""
import random
from typing import List, Dict, Any
from core.schemas.entity import UserProfile, MerchantProfile, DeviceFingerprint
from core.schemas.transaction import TransactionCreate, TransactionType
from core.utils.helpers import generate_id, utc_now

class Dataset:
    def __init__(self, users, merchants, devices, transactions):
        self.users = users
        self.merchants = merchants
        self.devices = devices
        self.transactions = transactions

class SyntheticDataGenerator:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        
    def generate_users(self, n: int = 1000) -> List[UserProfile]:
        users = []
        for i in range(n):
            users.append(UserProfile(
                id=f"user_{i}",
                created_at=str(utc_now()),
                updated_at=str(utc_now()),
                risk_score=random.uniform(0.0, 0.1)
            ))
        return users

    def generate_merchants(self, n: int = 200) -> List[MerchantProfile]:
        merchants = []
        categories = ["retail", "grocery", "travel", "digital", "gaming"]
        for i in range(n):
            merchants.append(MerchantProfile(
                id=f"merchant_{i}",
                created_at=str(utc_now()),
                updated_at=str(utc_now()),
                category=random.choice(categories)
            ))
        return merchants

    def generate_devices(self, users: List[UserProfile], avg_per_user: int = 2) -> List[DeviceFingerprint]:
        devices = []
        for user in users:
            num_devices = max(1, int(random.gauss(avg_per_user, 1)))
            for j in range(num_devices):
                devices.append(DeviceFingerprint(
                    id=f"device_{user.id}_{j}",
                    ip_address=f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                    user_agent="SyntheticBrowser/1.0"
                ))
        return devices

    def generate_transactions(
        self, users: List[UserProfile], merchants: List[MerchantProfile], devices: List[DeviceFingerprint], n: int = 50000, fraud_rate: float = 0.02
    ) -> List[TransactionCreate]:
        transactions = []
        for _ in range(n):
            is_fraud = random.random() < fraud_rate
            user = random.choice(users)
            merchant = random.choice(merchants)
            
            amount = random.expovariate(1/50) if not is_fraud else random.expovariate(1/500) + 100
            
            transactions.append(TransactionCreate(
                type=TransactionType.PURCHASE,
                amount=round(amount, 2),
                currency="USD",
                timestamp=utc_now(), # Note: would generate temporal distribution in deep implementation
                metadata={
                    "user_id": user.id,
                    "merchant_id": merchant.id,
                    "is_fraud": is_fraud
                }
            ))
        return transactions

    def generate_full_dataset(self, n_users: int = 1000, n_transactions: int = 50000) -> Dataset:
        users = self.generate_users(n_users)
        merchants = self.generate_merchants(int(n_users/5))
        devices = self.generate_devices(users)
        transactions = self.generate_transactions(users, merchants, devices, n_transactions)
        
        return Dataset(users, merchants, devices, transactions)
