"""AegisOS SDK Client — OpenAI-style resource-based client."""
from typing import Optional

import httpx

from packages.sdk_python.resources.transactions import TransactionsResource
from packages.sdk_python.resources.investigations import InvestigationsResource
from packages.sdk_python.resources.graph import GraphResource


class AegisClient:
    """Client for the AegisOS fraud intelligence platform.

    Usage:
        client = AegisClient(base_url="http://localhost:8000")
        result = client.transactions.score(amount=15000, sender_id="user_123")
        print(result.risk_score)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._http = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )
        self._async_http = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

        self.transactions = TransactionsResource(self._http, self._async_http)
        self.investigations = InvestigationsResource(self._http, self._async_http)
        self.graph = GraphResource(self._http, self._async_http)

    def health(self) -> dict:
        resp = self._http.get("/health")
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._http.close()

    async def aclose(self):
        await self._async_http.aclose()
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()
