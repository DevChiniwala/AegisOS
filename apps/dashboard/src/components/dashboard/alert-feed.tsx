"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { RiskBadge } from "@/components/shared/risk-badge";
import { AlertTriangle } from "lucide-react";
import type { TopRisk } from "@/types/api";

interface AlertFeedProps {
  alerts: TopRisk[];
}

export function AlertFeed({ alerts }: AlertFeedProps) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-risk-very-high" />
          Top Risk Entities
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[320px]">
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.entity_id}
                className="flex flex-col gap-1.5 rounded-lg border p-3 transition-colors hover:bg-accent/50"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{alert.name}</span>
                  <RiskBadge
                    level={
                      alert.risk_score >= 0.9
                        ? "CRITICAL"
                        : alert.risk_score >= 0.8
                        ? "VERY_HIGH"
                        : "HIGH"
                    }
                  />
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {alert.reason}
                </p>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span className="capitalize">{alert.entity_type}</span>
                  <span className="font-mono">
                    Score: {(alert.risk_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
