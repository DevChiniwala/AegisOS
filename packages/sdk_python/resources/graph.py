"""Graph resource for the AegisOS SDK."""
import httpx

from packages.sdk_python.models import Entity, FraudRing, GraphSubgraph


class GraphResource:
    def __init__(self, http: httpx.Client, async_http: httpx.AsyncClient):
        self._http = http
        self._async_http = async_http

    def entity(self, entity_id: str) -> Entity:
        resp = self._http.get(f"/api/v1/graph/entity/{entity_id}")
        resp.raise_for_status()
        return Entity(**resp.json())

    async def aentity(self, entity_id: str) -> Entity:
        resp = await self._async_http.get(f"/api/v1/graph/entity/{entity_id}")
        resp.raise_for_status()
        return Entity(**resp.json())

    def subgraph(self, entity_id: str, depth: int = 2) -> GraphSubgraph:
        resp = self._http.get(
            f"/api/v1/graph/subgraph/{entity_id}",
            params={"depth": depth},
        )
        resp.raise_for_status()
        return GraphSubgraph(**resp.json())

    def fraud_rings(self, min_size: int = 3) -> list[FraudRing]:
        resp = self._http.get(
            "/api/v1/graph/fraud-rings",
            params={"min_size": min_size},
        )
        resp.raise_for_status()
        return [FraudRing(**item) for item in resp.json()]

    async def afraud_rings(self, min_size: int = 3) -> list[FraudRing]:
        resp = await self._async_http.get(
            "/api/v1/graph/fraud-rings",
            params={"min_size": min_size},
        )
        resp.raise_for_status()
        return [FraudRing(**item) for item in resp.json()]

    def trace_money_flow(self, entity_id: str, max_hops: int = 5) -> GraphSubgraph:
        resp = self._http.post(
            "/api/v1/graph/trace",
            json={"entity_id": entity_id, "max_hops": max_hops},
        )
        resp.raise_for_status()
        return GraphSubgraph(**resp.json())
