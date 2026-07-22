from typing import List, Dict, Any
from core.schemas.transaction import TransactionCreate
from core.utils.helpers import generate_id
from core.utils.logging import get_logger
from .store import GraphStore
from .schema import GraphNode, GraphEdge, NodeType, EdgeType
import uuid

logger = get_logger(__name__)

class GraphIntelligenceEngine:
    def __init__(self, store: GraphStore):
        self.store = store

    async def add_transaction_to_graph(self, transaction: TransactionCreate) -> None:
        # Create Nodes
        tx_node = GraphNode(
            node_id=transaction.transaction_id or str(uuid.uuid4()),
            node_type=NodeType.TRANSACTION,
            properties=transaction.model_dump()
        )
        await self.store.add_node(tx_node)

        if transaction.user_id:
            user_node = GraphNode(node_id=transaction.user_id, node_type=NodeType.USER)
            await self.store.add_node(user_node)
            await self.store.add_edge(GraphEdge(
                edge_id=str(uuid.uuid4()), source_id=user_node.node_id, target_id=tx_node.node_id, edge_type=EdgeType.PAID_TO
            ))

        if transaction.merchant_id:
            merchant_node = GraphNode(node_id=transaction.merchant_id, node_type=NodeType.MERCHANT)
            await self.store.add_node(merchant_node)
            await self.store.add_edge(GraphEdge(
                edge_id=str(uuid.uuid4()), source_id=tx_node.node_id, target_id=merchant_node.node_id, edge_type=EdgeType.TRANSFERRED_TO
            ))
            
        if transaction.device_id:
            device_node = GraphNode(node_id=transaction.device_id, node_type=NodeType.DEVICE)
            await self.store.add_node(device_node)
            if transaction.user_id:
                await self.store.add_edge(GraphEdge(
                    edge_id=str(uuid.uuid4()), source_id=transaction.user_id, target_id=device_node.node_id, edge_type=EdgeType.OWNS
                ))
                
        if transaction.ip_address:
            ip_node = GraphNode(node_id=transaction.ip_address, node_type=NodeType.IP_ADDRESS)
            await self.store.add_node(ip_node)
            if transaction.user_id:
                await self.store.add_edge(GraphEdge(
                    edge_id=str(uuid.uuid4()), source_id=transaction.user_id, target_id=ip_node.node_id, edge_type=EdgeType.LOGGED_IN_FROM
                ))

    async def get_entity_subgraph(self, entity_id: str, depth: int = 2) -> Dict[str, Any]:
        return await self.store.query_subgraph(entity_id, depth)

    async def detect_fraud_rings(self, min_size: int = 3) -> List[List[str]]:
        # This would typically use networkx locally on a snapshot, or graph algos plugin in Neo4j.
        # Implemented in algorithms module.
        pass

    async def compute_risk_propagation(self, entity_id: str) -> float:
        # Placeholder for propagation logic implemented in algorithms.risk_propagation
        return 0.5

    async def find_money_flow_path(self, source_id: str, target_id: str) -> List[str]:
        # Implemented in algorithms module
        return [source_id, target_id]

    async def get_entity_risk_score(self, entity_id: str) -> float:
        node = await self.store.get_node(entity_id)
        return node.risk_score if node else 0.0

    async def get_shared_entities(self, entity_id_1: str, entity_id_2: str) -> Dict[str, Any]:
        neighbors_1 = set([n.node_id for n in await self.store.get_neighbors(entity_id_1)])
        neighbors_2 = set([n.node_id for n in await self.store.get_neighbors(entity_id_2)])
        
        shared_ids = neighbors_1.intersection(neighbors_2)
        shared_nodes = []
        for n_id in shared_ids:
            n = await self.store.get_node(n_id)
            if n: shared_nodes.append(n)
            
        return {"shared_nodes": shared_nodes}
