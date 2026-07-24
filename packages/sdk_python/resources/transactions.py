"""Transactions resource for the AegisOS SDK."""
from typing import Optional
from uuid import uuid4

import httpx

from packages.sdk_python.models import RiskScore


class TransactionsResource:
    def __init__(self, http: httpx.Client, async_http: httpx.AsyncClient):
        self._http = http
        self._async_http = async_http

    def score(
        self,
        amount: float,
        sender_id: str = "unknown",
        receiver_id: str = "unknown",
        currency: str = "USD",
        channel: str = "online",
        transaction_id: Optional[str] = None,
        **kwargs,
    ) -> RiskScore:
        payload = {
            "transaction_id": transaction_id or str(uuid4()),
            "amount": amount,
            "currency": currency,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "channel": channel,
            **kwargs,
        }
        resp = self._http.post("/api/v1/transactions/score", json=payload)
        resp.raise_for_status()
        return RiskScore(**resp.json())

    async def ascore(
        self,
        amount: float,
        sender_id: str = "unknown",
        receiver_id: str = "unknown",
        currency: str = "USD",
        channel: str = "online",
        transaction_id: Optional[str] = None,
        **kwargs,
    ) -> RiskScore:
        payload = {
            "transaction_id": transaction_id or str(uuid4()),
            "amount": amount,
            "currency": currency,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "channel": channel,
            **kwargs,
        }
        resp = await self._async_http.post("/api/v1/transactions/score", json=payload)
        resp.raise_for_status()
        return RiskScore(**resp.json())

    def score_batch(self, transactions: list[dict]) -> list[RiskScore]:
        resp = self._http.post("/api/v1/transactions/score/batch", json=transactions)
        resp.raise_for_status()
        return [RiskScore(**item) for item in resp.json()]

    def get(self, transaction_id: str) -> dict:
        resp = self._http.get(f"/api/v1/transactions/{transaction_id}")
        resp.raise_for_status()
        return resp.json()
