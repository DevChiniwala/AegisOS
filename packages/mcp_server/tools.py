"""MCP Tool definitions for AegisOS fraud intelligence operations."""
from typing import Any

import httpx

API_BASE = "http://localhost:8000"

TOOLS = [
    {
        "name": "score_transaction",
        "description": "Score a financial transaction for fraud risk. Returns a risk score (0-1), risk level, and explanation of contributing factors.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Transaction amount"},
                "sender_id": {"type": "string", "description": "Sender account/user ID"},
                "receiver_id": {"type": "string", "description": "Receiver account/merchant ID"},
                "currency": {"type": "string", "description": "Currency code (e.g. USD, EUR)", "default": "USD"},
                "channel": {"type": "string", "description": "Transaction channel (online, mobile, pos, atm, wire)", "default": "online"},
            },
            "required": ["amount", "sender_id", "receiver_id"],
        },
    },
    {
        "name": "trace_money_flow",
        "description": "Trace the flow of money from an entity through the transaction network. Reveals layering patterns, circular flows, and suspicious routing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Starting entity ID to trace from"},
                "max_hops": {"type": "integer", "description": "Maximum depth of trace (1-10)", "default": 5},
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "detect_fraud_rings",
        "description": "Detect fraud ring communities in the transaction graph using community detection algorithms. Returns groups of connected entities exhibiting coordinated suspicious behavior.",
        "input_schema": {
            "type": "object",
            "properties": {
                "min_size": {"type": "integer", "description": "Minimum ring size to report", "default": 3},
            },
        },
    },
    {
        "name": "screen_sanctions",
        "description": "Screen an entity against OFAC/PEP sanctions lists and adverse media databases. Returns match results with confidence scores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_name": {"type": "string", "description": "Name of entity to screen"},
                "entity_type": {"type": "string", "description": "Type: person, company, or account", "default": "person"},
                "country": {"type": "string", "description": "Country code for focused screening"},
            },
            "required": ["entity_name"],
        },
    },
    {
        "name": "investigate_transaction",
        "description": "Launch a full multi-agent investigation on a transaction. Deploys 12 specialized AI agents (graph detective, behavior analyst, compliance officer, etc.) to analyze the transaction from every angle. Returns a comprehensive verdict with evidence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "Transaction ID to investigate"},
            },
            "required": ["transaction_id"],
        },
    },
    {
        "name": "generate_sar",
        "description": "Generate a Suspicious Activity Report (SAR) narrative for a completed investigation. Produces FinCEN-compliant narrative text with supporting evidence citations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string", "description": "Investigation case ID"},
                "include_evidence": {"type": "boolean", "description": "Include detailed evidence section", "default": True},
            },
            "required": ["case_id"],
        },
    },
]


async def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute an MCP tool and return the result."""
    handlers = {
        "score_transaction": _score_transaction,
        "trace_money_flow": _trace_money_flow,
        "detect_fraud_rings": _detect_fraud_rings,
        "screen_sanctions": _screen_sanctions,
        "investigate_transaction": _investigate_transaction,
        "generate_sar": _generate_sar,
    }

    handler = handlers.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}

    try:
        return await handler(arguments)
    except httpx.ConnectError:
        return {"error": "Cannot connect to AegisOS API. Ensure the server is running (aegis serve)."}
    except httpx.HTTPStatusError as e:
        return {"error": f"API error {e.response.status_code}: {e.response.text}"}


async def _score_transaction(args: dict) -> dict:
    from uuid import uuid4

    payload = {
        "transaction_id": str(uuid4()),
        "amount": args["amount"],
        "sender_id": args["sender_id"],
        "receiver_id": args["receiver_id"],
        "currency": args.get("currency", "USD"),
        "channel": args.get("channel", "online"),
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/api/v1/transactions/score", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()


async def _trace_money_flow(args: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/api/v1/graph/trace",
            json={"entity_id": args["entity_id"], "max_hops": args.get("max_hops", 5)},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


async def _detect_fraud_rings(args: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{API_BASE}/api/v1/graph/fraud-rings",
            params={"min_size": args.get("min_size", 3)},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


async def _screen_sanctions(args: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/api/v1/compliance/screen",
            json={
                "entity_name": args["entity_name"],
                "entity_type": args.get("entity_type", "person"),
                "country": args.get("country"),
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


async def _investigate_transaction(args: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/api/v1/investigations/",
            json={"transaction_id": args["transaction_id"]},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()


async def _generate_sar(args: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_BASE}/api/v1/investigations/{args['case_id']}/sar",
            json={"include_evidence": args.get("include_evidence", True)},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
