"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Activity, ShieldAlert, Zap, AlertTriangle } from "lucide-react";

interface LiveStatsProps {
  txPerSecond: number;
  avgRisk: number;
  fraudRate: number;
  alertsTriggered: number;
}

export function LiveStats({ txPerSecond, avgRisk, fraudRate, alertsTriggered }: LiveStatsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <Card>
        <CardContent className="p-4 flex items-center gap-3">
          <Zap className="h-5 w-5 text-primary" />
          <div>
            <p className="text-xs text-muted-foreground">Tx/sec</p>
            <p className="text-lg font-bold font-mono">{txPerSecond.toFixed(1)}</p>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 flex items-center gap-3">
          <Activity className="h-5 w-5 text-risk-medium" />
          <div>
            <p className="text-xs text-muted-foreground">Avg Risk</p>
            <p className="text-lg font-bold font-mono">{(avgRisk * 100).toFixed(1)}%</p>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 flex items-center gap-3">
          <ShieldAlert className="h-5 w-5 text-risk-very-high" />
          <div>
            <p className="text-xs text-muted-foreground">Fraud Rate</p>
            <p className="text-lg font-bold font-mono">{(fraudRate * 100).toFixed(2)}%</p>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-risk-high" />
          <div>
            <p className="text-xs text-muted-foreground">Alerts</p>
            <p className="text-lg font-bold font-mono">{alertsTriggered}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
