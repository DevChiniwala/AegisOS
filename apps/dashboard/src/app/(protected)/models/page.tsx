"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchModelPerformance } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from "recharts";
import { RefreshCw, Activity, Clock, Cpu } from "lucide-react";

export default function ModelsPage() {
  const { data: models } = useQuery({
    queryKey: ["model-performance"],
    queryFn: fetchModelPerformance,
  });

  const barData = (models ?? []).map((m) => ({
    name: m.model_name.replace("Adaptive ", "").slice(0, 10),
    precision: +(m.precision * 100).toFixed(1),
    recall: +(m.recall * 100).toFixed(1),
    f1: +(m.f1 * 100).toFixed(1),
  }));

  const radarData = [
    { metric: "Precision", ...Object.fromEntries((models ?? []).map((m) => [m.model_name, m.precision * 100])) },
    { metric: "Recall", ...Object.fromEntries((models ?? []).map((m) => [m.model_name, m.recall * 100])) },
    { metric: "F1", ...Object.fromEntries((models ?? []).map((m) => [m.model_name, m.f1 * 100])) },
    { metric: "AUC", ...Object.fromEntries((models ?? []).map((m) => [m.model_name, m.auc * 100])) },
    { metric: "Accuracy", ...Object.fromEntries((models ?? []).map((m) => [m.model_name, m.accuracy * 100])) },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Model Monitoring</h1>
        <p className="text-muted-foreground">
          ML model performance metrics and health
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        {(models ?? []).map((model) => (
          <Card key={model.model_name}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <Cpu className="h-5 w-5 text-primary" />
                <Badge variant="success" className="text-[10px]">Active</Badge>
              </div>
              <p className="text-sm font-medium truncate">{model.model_name}</p>
              <div className="mt-2 space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">F1 Score</span>
                  <span className="font-mono font-medium">{(model.f1 * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Latency P50</span>
                  <span className="font-mono font-medium">{model.latency_p50}ms</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">AUC</span>
                  <span className="font-mono font-medium">{(model.auc * 100).toFixed(1)}%</span>
                </div>
              </div>
              <Button variant="outline" size="sm" className="w-full mt-3 text-xs">
                <RefreshCw className="h-3 w-3 mr-1" />
                Reload
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Performance Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 33%, 17%)" />
                  <XAxis dataKey="name" stroke="hsl(215, 20%, 65%)" fontSize={11} />
                  <YAxis stroke="hsl(215, 20%, 65%)" fontSize={11} domain={[70, 100]} />
                  <Tooltip contentStyle={{ backgroundColor: "hsl(222, 47%, 8%)", border: "1px solid hsl(217, 33%, 17%)", borderRadius: "8px", color: "hsl(210, 40%, 98%)" }} />
                  <Bar dataKey="precision" fill="hsl(217, 91%, 60%)" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="recall" fill="hsl(142, 76%, 36%)" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="f1" fill="hsl(38, 92%, 50%)" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Inference Latency (ms)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 mt-4">
              {(models ?? []).map((model) => (
                <div key={model.model_name} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground truncate max-w-[150px]">
                      {model.model_name}
                    </span>
                    <div className="flex gap-3 text-xs font-mono">
                      <span>P50: {model.latency_p50}ms</span>
                      <span>P95: {model.latency_p95}ms</span>
                      <span className="text-muted-foreground">P99: {model.latency_p99}ms</span>
                    </div>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${Math.min((model.latency_p99 / 50) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
