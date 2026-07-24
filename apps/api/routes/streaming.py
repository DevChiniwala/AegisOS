"""
Streaming endpoints (WebSockets) — Real-time transaction scoring and investigation feeds.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse
from typing import List
from pydantic import BaseModel

from core.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.transaction_connections: List[WebSocket] = []
        self.alert_connections: List[WebSocket] = []
        self.investigation_connections: dict[str, List[WebSocket]] = {}

    async def connect_transactions(self, websocket: WebSocket):
        await websocket.accept()
        self.transaction_connections.append(websocket)

    async def connect_alerts(self, websocket: WebSocket):
        await websocket.accept()
        self.alert_connections.append(websocket)

    async def connect_investigation(self, websocket: WebSocket, case_id: str):
        await websocket.accept()
        if case_id not in self.investigation_connections:
            self.investigation_connections[case_id] = []
        self.investigation_connections[case_id].append(websocket)

    def disconnect_transactions(self, websocket: WebSocket):
        if websocket in self.transaction_connections:
            self.transaction_connections.remove(websocket)

    def disconnect_alerts(self, websocket: WebSocket):
        if websocket in self.alert_connections:
            self.alert_connections.remove(websocket)

    def disconnect_investigation(self, websocket: WebSocket, case_id: str):
        if case_id in self.investigation_connections:
            if websocket in self.investigation_connections[case_id]:
                self.investigation_connections[case_id].remove(websocket)

    async def broadcast_transaction(self, message: dict):
        dead = []
        for conn in self.transaction_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.transaction_connections.remove(d)

    async def broadcast_alert(self, message: dict):
        dead = []
        for conn in self.alert_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.alert_connections.remove(d)

    async def broadcast_investigation_event(self, case_id: str, message: dict):
        connections = self.investigation_connections.get(case_id, [])
        dead = []
        for conn in connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            connections.remove(d)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return manager


@router.websocket("/transactions")
async def websocket_transactions(websocket: WebSocket):
    """Real-time scored transaction feed."""
    await manager.connect_transactions(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_transactions(websocket)


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    """Real-time alerts feed for high-risk transactions."""
    await manager.connect_alerts(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_alerts(websocket)


@router.websocket("/investigations/{case_id}")
async def websocket_investigation(websocket: WebSocket, case_id: str):
    """Real-time investigation progress feed."""
    await manager.connect_investigation(websocket, case_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_investigation(websocket, case_id)


class InvestigationStreamRequest(BaseModel):
    transaction_id: str


@router.post("/investigations/stream")
async def stream_investigation(body: InvestigationStreamRequest, request: Request):
    """SSE endpoint for streaming investigation agent activity."""
    from services.agents.langgraph_orchestrator import LangGraphOrchestrator
    from core.schemas.transaction import TransactionCreate

    orchestrator = LangGraphOrchestrator()
    if not orchestrator.available:
        return StreamingResponse(
            iter([json.dumps({"type": "error", "message": "LangGraph not available"}) + "\n"]),
            media_type="application/x-ndjson",
        )

    tx = TransactionCreate(
        transaction_id=body.transaction_id,
        amount=0,
        currency="USD",
        sender_id="unknown",
        receiver_id="unknown",
        channel="api",
    )

    risk_engine = request.app.state.risk_engine
    feature_engine = request.app.state.feature_engine
    features = feature_engine.extract_features(transaction=tx, user=None, merchant=None, device=None, history=[])
    result = risk_engine.score_transaction(tx, features)

    async def event_generator():
        async for event in orchestrator.stream_investigation(tx, result.score, features):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
