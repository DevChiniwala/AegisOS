export type NodeType = "user" | "merchant" | "device" | "account" | "ip" | "card";

export type EdgeType =
  | "paid_to"
  | "owns"
  | "connected_to"
  | "shares_device"
  | "shares_ip"
  | "same_location"
  | "same_email"
  | "same_phone"
  | "same_merchant"
  | "transferred_to";

export interface GraphNode {
  id: string;
  type: NodeType;
  label: string;
  risk_score: number;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  weight: number;
  properties?: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Community {
  community_id: string;
  size: number;
  risk_score: number;
  node_ids: string[];
  label?: string;
}
