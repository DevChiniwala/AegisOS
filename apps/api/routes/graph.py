"""
Graph endpoints — wired to GraphIntelligenceEngine.
"""
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/entity/{entity_id}")
async def get_entity_subgraph(entity_id: str, request: Request):
    """Get the subgraph around an entity."""
    graph_engine = request.app.state.graph_engine
    subgraph = await graph_engine.get_entity_subgraph(entity_id)
    return subgraph


@router.get("/communities")
async def list_communities(request: Request):
    """Detect fraud ring communities."""
    graph_engine = request.app.state.graph_engine
    communities = await graph_engine.detect_fraud_rings()
    return communities


@router.get("/path/{source_id}/{target_id}")
async def find_path(source_id: str, target_id: str, request: Request):
    """Find money flow path between two entities."""
    graph_engine = request.app.state.graph_engine
    path = await graph_engine.find_money_flow_path(source_id, target_id)
    return {"path": path}


@router.get("/risk-propagation/{entity_id}")
async def get_risk_propagation(entity_id: str, request: Request):
    """Get propagated risk score for an entity."""
    graph_engine = request.app.state.graph_engine
    risk = await graph_engine.get_entity_risk_score(entity_id)
    return {"entity_id": entity_id, "propagated_risk": risk}


@router.get("/stats")
async def get_graph_stats(request: Request):
    """Get graph statistics."""
    graph_engine = request.app.state.graph_engine
    store = graph_engine.store
    if hasattr(store, '_graph'):
        return {
            "node_count": store._graph.number_of_nodes(),
            "edge_count": store._graph.number_of_edges(),
        }
    return {"node_count": 0, "edge_count": 0}
