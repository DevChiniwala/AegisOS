from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class NodeType(str, Enum):
    USER = "USER"
    DEVICE = "DEVICE"
    CARD = "CARD"
    ACCOUNT = "ACCOUNT"
    MERCHANT = "MERCHANT"
    IP_ADDRESS = "IP_ADDRESS"
    LOCATION = "LOCATION"
    TRANSACTION = "TRANSACTION"
    PHONE = "PHONE"
    EMAIL = "EMAIL"

class EdgeType(str, Enum):
    PAID_TO = "PAID_TO"
    OWNS = "OWNS"
    CONNECTED_TO = "CONNECTED_TO"
    SHARES_DEVICE = "SHARES_DEVICE"
    SHARES_IP = "SHARES_IP"
    SAME_LOCATION = "SAME_LOCATION"
    SAME_EMAIL = "SAME_EMAIL"
    SAME_PHONE = "SAME_PHONE"
    SAME_MERCHANT = "SAME_MERCHANT"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    LOGGED_IN_FROM = "LOGGED_IN_FROM"
    USED_CARD = "USED_CARD"

class GraphNode(BaseModel):
    node_id: str
    node_type: NodeType
    properties: Dict[str, Any] = Field(default_factory=dict)
    risk_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GraphEdge(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: Dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
