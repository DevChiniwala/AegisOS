"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ConnectionStatus } from "@/components/live/connection-status";
import { LiveFeed } from "@/components/live/live-feed";
import { LiveStats } from "@/components/live/live-stats";
import { useWebSocket } from "@/hooks/use-websocket";
import { WS_BASE_URL } from "@/lib/constants";
import { mockTransactions } from "@/lib/mock-data";
import { Pause, Play, Radio } from "lucide-react";
import type { Transaction } from "@/types/transaction";

export default function LivePage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [paused, setPaused] = useState(false);
  const [stats, setStats] = useState({
    txPerSecond: 0,
    avgRisk: 0,
    fraudRate: 0,
    alertsTriggered: 0,
  });
  const simulationRef = useRef<NodeJS.Timeout>();

  const handleMessage = useCallback(
    (data: unknown) => {
      if (paused) return;
      const tx = data as Transaction;
      setTransactions((prev) => [tx, ...prev].slice(0, 100));
    },
    [paused]
  );

  const { status } = useWebSocket({
    url: `${WS_BASE_URL}/api/v1/ws/transactions`,
    onMessage: handleMessage,
  });

  useEffect(() => {
    if (status !== "connected") {
      simulationRef.current = setInterval(() => {
        if (paused) return;
        const mockTx = mockTransactions[Math.floor(Math.random() * mockTransactions.length)];
        const simulated: Transaction = {
          ...mockTx,
          transaction_id: `txn_sim_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
          timestamp: new Date().toISOString(),
          amount: mockTx.amount * (0.5 + Math.random()),
        };
        setTransactions((prev) => [simulated, ...prev].slice(0, 100));
      }, 800 + Math.random() * 1200);
    }

    return () => {
      if (simulationRef.current) clearInterval(simulationRef.current);
    };
  }, [status, paused]);

  useEffect(() => {
    const recent = transactions.slice(0, 20);
    if (recent.length === 0) return;
    const avgRisk = recent.reduce((sum, t) => sum + (t.risk_score ?? 0), 0) / recent.length;
    const fraudCount = recent.filter((t) => (t.risk_score ?? 0) >= 0.7).length;
    setStats({
      txPerSecond: Math.max(0.5, 1 + Math.random()),
      avgRisk,
      fraudRate: fraudCount / Math.max(recent.length, 1),
      alertsTriggered: transactions.filter((t) => (t.risk_score ?? 0) >= 0.8).length,
    });
  }, [transactions]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Radio className="h-7 w-7 text-primary" />
            Live Feed
          </h1>
          <p className="text-muted-foreground">
            Real-time transaction scoring stream
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ConnectionStatus status={status === "connected" ? "connected" : "disconnected"} />
          <Button
            variant={paused ? "default" : "outline"}
            size="sm"
            onClick={() => setPaused(!paused)}
          >
            {paused ? <Play className="h-4 w-4 mr-1" /> : <Pause className="h-4 w-4 mr-1" />}
            {paused ? "Resume" : "Pause"}
          </Button>
        </div>
      </div>

      <LiveStats {...stats} />

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center justify-between">
            <span>Transaction Stream</span>
            <span className="text-xs font-normal text-muted-foreground">
              {transactions.length} transactions buffered
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <LiveFeed transactions={transactions} paused={paused} />
        </CardContent>
      </Card>
    </div>
  );
}
