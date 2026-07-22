from typing import Protocol, List, Dict, Any, Optional
import threading
import networkx as nx
from neo4j import AsyncGraphDatabase
from datetime import datetime

from .schema import GraphNode, GraphEdge, NodeType, EdgeType
from core.utils.logging import get_logger

logger = get_logger(__name__)

class GraphStore(Protocol):
    async def add_node(self, node: GraphNode) -> None: ...
    async def add_edge(self, edge: GraphEdge) -> None: ...
    async def get_node(self, node_id: str) -> Optional[GraphNode]: ...
    async def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[GraphNode]: ...
    async def get_edges(self, source_id: str, target_id: Optional[str] = None) -> List[GraphEdge]: ...
    async def query_subgraph(self, node_id: str, depth: int = 2) -> Dict[str, Any]: ...
    async def update_node_property(self, node_id: str, key: str, value: Any) -> None: ...

class NetworkXGraphStore:
    def __init__(self):
        self._graph = nx.MultiDiGraph()
        self._lock = threading.Lock()

    async def add_node(self, node: GraphNode) -> None:
        with self._lock:
            self._graph.add_node(
                node.node_id,
                **node.model_dump()
            )

    async def add_edge(self, edge: GraphEdge) -> None:
        with self._lock:
            self._graph.add_edge(
                edge.source_id,
                edge.target_id,
                key=edge.edge_id,
                **edge.model_dump()
            )

    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        with self._lock:
            if self._graph.has_node(node_id):
                data = self._graph.nodes[node_id]
                return GraphNode(**data)
            return None

    async def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[GraphNode]:
        neighbors = []
        with self._lock:
            if not self._graph.has_node(node_id):
                return []
            for neighbor in self._graph.neighbors(node_id):
                if edge_type:
                    edges = self._graph.get_edge_data(node_id, neighbor)
                    if not any(e.get('edge_type') == edge_type.value for e in edges.values()):
                        continue
                neighbors.append(GraphNode(**self._graph.nodes[neighbor]))
        return neighbors

    async def get_edges(self, source_id: str, target_id: Optional[str] = None) -> List[GraphEdge]:
        edges = []
        with self._lock:
            if not self._graph.has_node(source_id):
                return []
            if target_id and self._graph.has_node(target_id):
                edge_data = self._graph.get_edge_data(source_id, target_id)
                if edge_data:
                    for key, data in edge_data.items():
                        edges.append(GraphEdge(**data))
            elif not target_id:
                for u, v, data in self._graph.out_edges(source_id, data=True):
                    edges.append(GraphEdge(**data))
        return edges

    async def query_subgraph(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        with self._lock:
            if not self._graph.has_node(node_id):
                return {"nodes": [], "edges": []}
            
            subgraph_nodes = set([node_id])
            current_layer = set([node_id])
            
            for _ in range(depth):
                next_layer = set()
                for n in current_layer:
                    next_layer.update(self._graph.successors(n))
                    next_layer.update(self._graph.predecessors(n))
                subgraph_nodes.update(next_layer)
                current_layer = next_layer
                
            subgraph = self._graph.subgraph(subgraph_nodes)
            nodes = [GraphNode(**data) for _, data in subgraph.nodes(data=True)]
            edges = [GraphEdge(**data) for _, _, data in subgraph.edges(data=True)]
            
            return {"nodes": nodes, "edges": edges}

    async def update_node_property(self, node_id: str, key: str, value: Any) -> None:
        with self._lock:
            if self._graph.has_node(node_id):
                self._graph.nodes[node_id][key] = value
                self._graph.nodes[node_id]['updated_at'] = datetime.utcnow()

class Neo4jGraphStore:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        
    async def close(self):
        await self._driver.close()

    async def add_node(self, node: GraphNode) -> None:
        query = """
        MERGE (n:Node {node_id: $node_id})
        SET n += $props, n.node_type = $node_type
        """
        props = node.model_dump()
        props['created_at'] = props['created_at'].isoformat()
        props['updated_at'] = props['updated_at'].isoformat()
        
        async with self._driver.session() as session:
            await session.run(query, node_id=node.node_id, props=props, node_type=node.node_type.value)

    async def add_edge(self, edge: GraphEdge) -> None:
        query = f"""
        MATCH (s:Node {{node_id: $source_id}})
        MATCH (t:Node {{node_id: $target_id}})
        MERGE (s)-[r:{edge.edge_type.value} {{edge_id: $edge_id}}]->(t)
        SET r += $props
        """
        props = edge.model_dump()
        props['timestamp'] = props['timestamp'].isoformat()
        
        async with self._driver.session() as session:
            await session.run(query, source_id=edge.source_id, target_id=edge.target_id, 
                              edge_id=edge.edge_id, props=props)

    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        query = "MATCH (n:Node {node_id: $node_id}) RETURN n"
        async with self._driver.session() as session:
            result = await session.run(query, node_id=node_id)
            record = await result.single()
            if record:
                data = dict(record['n'])
                return GraphNode(**data)
            return None

    async def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[GraphNode]:
        rel = f":{edge_type.value}" if edge_type else ""
        query = f"MATCH (n:Node {{node_id: $node_id}})-[{rel}]-(m:Node) RETURN m"
        async with self._driver.session() as session:
            result = await session.run(query, node_id=node_id)
            records = await result.data()
            return [GraphNode(**r['m']) for r in records]

    async def get_edges(self, source_id: str, target_id: Optional[str] = None) -> List[GraphEdge]:
        if target_id:
            query = "MATCH (s:Node {node_id: $source_id})-[r]->(t:Node {node_id: $target_id}) RETURN r, s.node_id as source_id, t.node_id as target_id"
            params = {"source_id": source_id, "target_id": target_id}
        else:
            query = "MATCH (s:Node {node_id: $source_id})-[r]->(t:Node) RETURN r, s.node_id as source_id, t.node_id as target_id"
            params = {"source_id": source_id}
            
        async with self._driver.session() as session:
            result = await session.run(query, **params)
            records = await result.data()
            edges = []
            for record in records:
                edge_data = dict(record['r'])
                edge_data['source_id'] = record['source_id']
                edge_data['target_id'] = record['target_id']
                edges.append(GraphEdge(**edge_data))
            return edges

    async def query_subgraph(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        query = f"""
        MATCH p=(n:Node {{node_id: $node_id}})-[*1..{depth}]-(m:Node)
        RETURN nodes(p) as nodes, relationships(p) as edges
        """
        async with self._driver.session() as session:
            result = await session.run(query, node_id=node_id)
            records = await result.data()
            
            unique_nodes = {}
            unique_edges = {}
            
            for record in records:
                for node in record['nodes']:
                    unique_nodes[node['node_id']] = dict(node)
                for edge in record['edges']:
                    unique_edges[edge['edge_id']] = dict(edge)
                    
            nodes = [GraphNode(**data) for data in unique_nodes.values()]
            edges = [GraphEdge(**data) for data in unique_edges.values()]
            return {"nodes": nodes, "edges": edges}

    async def update_node_property(self, node_id: str, key: str, value: Any) -> None:
        query = f"""
        MATCH (n:Node {{node_id: $node_id}})
        SET n.{key} = $value, n.updated_at = $timestamp
        """
        async with self._driver.session() as session:
            await session.run(query, node_id=node_id, value=value, timestamp=datetime.utcnow().isoformat())
