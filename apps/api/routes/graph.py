"""
Graph endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/entity/{entity_id}")
async def get_entity_subgraph(entity_id: str):
    return {"nodes": [], "edges": []}

@router.get("/communities")
async def list_communities():
    return []

@router.get("/path/{source_id}/{target_id}")
async def find_path(source_id: str, target_id: str):
    return {"path": []}

@router.get("/risk-propagation/{entity_id}")
async def get_risk_propagation(entity_id: str):
    return {"entity_id": entity_id, "propagated_risk": 0.5}

@router.get("/stats")
async def get_graph_stats():
    return {"node_count": 0, "edge_count": 0, "communities": 0}
