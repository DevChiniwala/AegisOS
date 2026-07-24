"""Investigations resource for the AegisOS SDK."""
from typing import AsyncIterator, Iterator

import httpx

from packages.sdk_python.models import Investigation


class InvestigationsResource:
    def __init__(self, http: httpx.Client, async_http: httpx.AsyncClient):
        self._http = http
        self._async_http = async_http

    def create(self, transaction_id: str) -> Investigation:
        resp = self._http.post(
            "/api/v1/investigations/",
            json={"transaction_id": transaction_id},
        )
        resp.raise_for_status()
        return Investigation(**resp.json())

    async def acreate(self, transaction_id: str) -> Investigation:
        resp = await self._async_http.post(
            "/api/v1/investigations/",
            json={"transaction_id": transaction_id},
        )
        resp.raise_for_status()
        return Investigation(**resp.json())

    def get(self, case_id: str) -> Investigation:
        resp = self._http.get(f"/api/v1/investigations/{case_id}")
        resp.raise_for_status()
        return Investigation(**resp.json())

    def list(self, limit: int = 50, offset: int = 0) -> list[Investigation]:
        resp = self._http.get(
            "/api/v1/investigations/",
            params={"limit": limit, "offset": offset},
        )
        resp.raise_for_status()
        return [Investigation(**item) for item in resp.json()]

    def stream(self, transaction_id: str) -> Iterator[dict]:
        """Stream agent activity during an investigation."""
        import json

        with self._http.stream(
            "POST",
            "/api/v1/investigations/stream",
            json={"transaction_id": transaction_id},
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    yield json.loads(line)

    async def astream(self, transaction_id: str) -> AsyncIterator[dict]:
        """Async stream agent activity during an investigation."""
        import json

        async with self._async_http.stream(
            "POST",
            "/api/v1/investigations/stream",
            json={"transaction_id": transaction_id},
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line:
                    yield json.loads(line)
