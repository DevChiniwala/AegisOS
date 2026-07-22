"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "reactflow";
import { User, Store, Smartphone, CreditCard, Globe, Wallet } from "lucide-react";
import { cn } from "@/lib/utils";
import type { NodeType } from "@/types/graph";

interface EntityNodeData {
  label: string;
  type: NodeType;
  risk_score: number;
}

const NODE_ICONS: Record<NodeType, typeof User> = {
  user: User,
  merchant: Store,
  device: Smartphone,
  card: CreditCard,
  ip: Globe,
  account: Wallet,
};

const NODE_SHAPES: Record<NodeType, string> = {
  user: "rounded-full",
  merchant: "rounded-lg",
  device: "rounded-lg rotate-45",
  card: "rounded-md",
  ip: "rounded-full",
  account: "rounded-md",
};

function getRiskRing(score: number): string {
  if (score >= 0.8) return "ring-2 ring-risk-very-high shadow-[0_0_12px_hsl(var(--risk-very-high)/0.4)]";
  if (score >= 0.5) return "ring-2 ring-risk-medium";
  if (score >= 0.3) return "ring-1 ring-risk-low";
  return "ring-1 ring-border";
}

function EntityNodeComponent({ data }: NodeProps<EntityNodeData>) {
  const Icon = NODE_ICONS[data.type] || User;
  const shape = NODE_SHAPES[data.type] || "rounded-full";

  return (
    <>
      <Handle type="target" position={Position.Top} className="!bg-primary !w-2 !h-2" />
      <div
        className={cn(
          "flex flex-col items-center gap-1 p-2 bg-card border cursor-pointer transition-all hover:scale-105",
          shape,
          getRiskRing(data.risk_score)
        )}
      >
        <div className={cn(
          "flex items-center justify-center w-10 h-10",
          data.type === "device" ? "-rotate-45" : ""
        )}>
          <Icon className="h-5 w-5 text-foreground" />
        </div>
      </div>
      <div className="text-center mt-1 max-w-[80px]">
        <p className="text-[10px] font-medium truncate">{data.label}</p>
        <p className="text-[9px] text-muted-foreground">
          {(data.risk_score * 100).toFixed(0)}%
        </p>
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-primary !w-2 !h-2" />
    </>
  );
}

export const EntityNode = memo(EntityNodeComponent);
