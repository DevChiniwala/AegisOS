"use client";

import { useCallback, useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type NodeTypes,
} from "reactflow";
import "reactflow/dist/style.css";
import { EntityNode } from "./entity-node";
import type { GraphData } from "@/types/graph";

interface GraphCanvasProps {
  data: GraphData;
  onNodeClick?: (nodeId: string) => void;
}

const nodeTypes: NodeTypes = {
  entity: EntityNode,
};

const EDGE_COLORS: Record<string, string> = {
  paid_to: "#3b82f6",
  owns: "#8b5cf6",
  connected_to: "#6b7280",
  shares_device: "#ef4444",
  shares_ip: "#f97316",
  same_location: "#22c55e",
  transferred_to: "#eab308",
  same_email: "#06b6d4",
  same_phone: "#ec4899",
  same_merchant: "#14b8a6",
};

function layoutNodes(data: GraphData): { nodes: Node[]; edges: Edge[] } {
  const angleStep = (2 * Math.PI) / Math.max(data.nodes.length, 1);
  const radius = Math.max(200, data.nodes.length * 40);

  const nodes: Node[] = data.nodes.map((node, i) => ({
    id: node.id,
    type: "entity",
    position: {
      x: 400 + radius * Math.cos(i * angleStep),
      y: 300 + radius * Math.sin(i * angleStep),
    },
    data: {
      label: node.label,
      type: node.type,
      risk_score: node.risk_score,
    },
  }));

  const edges: Edge[] = data.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.type.replace("_", " "),
    style: {
      stroke: EDGE_COLORS[edge.type] || "#6b7280",
      strokeWidth: Math.min(edge.weight + 1, 4),
    },
    labelStyle: { fontSize: 9, fill: "#9ca3af" },
    animated: edge.type === "transferred_to" || edge.type === "shares_device",
  }));

  return { nodes, edges };
}

export function GraphCanvas({ data, onNodeClick }: GraphCanvasProps) {
  const { nodes: initialNodes, edges: initialEdges } = useMemo(
    () => layoutNodes(data),
    [data]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      onNodeClick?.(node.id);
    },
    [onNodeClick]
  );

  return (
    <div className="h-[600px] w-full rounded-lg border bg-background">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.3}
        maxZoom={2}
        defaultEdgeOptions={{
          type: "smoothstep",
        }}
      >
        <Background color="hsl(217, 33%, 17%)" gap={20} />
        <Controls className="!bg-card !border-border [&>button]:!bg-card [&>button]:!border-border [&>button]:!text-foreground" />
        <MiniMap
          className="!bg-card !border-border"
          nodeColor={(node) => {
            const score = node.data?.risk_score ?? 0;
            if (score >= 0.8) return "hsl(0, 84%, 60%)";
            if (score >= 0.5) return "hsl(38, 92%, 50%)";
            return "hsl(142, 76%, 36%)";
          }}
        />
      </ReactFlow>
    </div>
  );
}
