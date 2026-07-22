"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ModelPerformance } from "@/types/api";

interface ModelSummaryProps {
  models: ModelPerformance[];
}

export function ModelSummary({ models }: ModelSummaryProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium">
          Model Performance
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {models.slice(0, 4).map((model) => (
            <div key={model.model_name} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-primary" />
                <span className="text-sm font-medium">{model.model_name}</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs font-mono">
                  F1: {model.f1.toFixed(2)}
                </Badge>
                <Badge variant="outline" className="text-xs font-mono">
                  P{50}: {model.latency_p50}ms
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
