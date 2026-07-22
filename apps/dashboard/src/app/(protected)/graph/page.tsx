"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";
import { fetchEntityGraph, fetchCommunities } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { RiskBadge } from "@/components/shared/risk-badge";
import { Search, Users } from "lucide-react";

const GraphCanvas = dynamic(
  () => import("@/components/graph/graph-canvas").then((m) => ({ default: m.GraphCanvas })),
  { ssr: false, loading: () => <div className="h-[600px] w-full rounded-lg border bg-background animate-pulse" /> }
);

export default function GraphPage() {
  const [searchEntity, setSearchEntity] = useState("usr_8d2f1");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const { data: graphData } = useQuery({
    queryKey: ["graph", searchEntity],
    queryFn: () => fetchEntityGraph(searchEntity),
  });

  const { data: communities } = useQuery({
    queryKey: ["communities"],
    queryFn: fetchCommunities,
  });

  const selectedNodeData = graphData?.nodes.find((n) => n.id === selectedNode);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Graph Explorer</h1>
        <p className="text-muted-foreground">
          Interactive entity relationship visualization
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Enter entity ID..."
            className="pl-9"
            value={searchEntity}
            onChange={(e) => setSearchEntity(e.target.value)}
          />
        </div>
        <Button size="sm">Load Graph</Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        <div className="lg:col-span-3">
          {graphData && (
            <GraphCanvas
              data={graphData}
              onNodeClick={(id) => setSelectedNode(id)}
            />
          )}
        </div>

        <div className="space-y-4">
          {selectedNodeData && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Node Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">ID</span>
                  <span className="font-mono text-xs">{selectedNodeData.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Type</span>
                  <Badge variant="outline" className="capitalize">{selectedNodeData.type}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Label</span>
                  <span className="font-medium">{selectedNodeData.label}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Risk</span>
                  <RiskBadge level={
                    selectedNodeData.risk_score >= 0.8 ? "VERY_HIGH" :
                    selectedNodeData.risk_score >= 0.5 ? "HIGH" :
                    selectedNodeData.risk_score >= 0.3 ? "MEDIUM" : "LOW"
                  } />
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Connections</span>
                  <span>{graphData?.edges.filter(e => e.source === selectedNodeData.id || e.target === selectedNodeData.id).length}</span>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Users className="h-4 w-4" />
                Fraud Communities
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[250px]">
                <div className="space-y-3">
                  {(communities ?? []).map((comm) => (
                    <div key={comm.community_id} className="rounded-md border p-3 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium">
                          {comm.size} nodes
                        </span>
                        <RiskBadge level={
                          comm.risk_score >= 0.8 ? "VERY_HIGH" : "HIGH"
                        } />
                      </div>
                      {comm.label && (
                        <p className="text-xs text-muted-foreground">{comm.label}</p>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Legend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#3b82f6]" />
                  <span>paid_to</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#ef4444]" />
                  <span>shares_device</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#f97316]" />
                  <span>shares_ip</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#eab308]" />
                  <span>transferred_to</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#8b5cf6]" />
                  <span>owns</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[#6b7280]" />
                  <span>connected_to</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
