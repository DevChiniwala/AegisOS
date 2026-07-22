"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Settings,
  Shield,
  Activity,
  Database,
  Server,
  CheckCircle,
  XCircle,
} from "lucide-react";

interface ServiceHealth {
  name: string;
  status: "healthy" | "degraded" | "unhealthy";
  latency: number;
}

const MOCK_SERVICES: ServiceHealth[] = [
  { name: "PostgreSQL", status: "healthy", latency: 2 },
  { name: "Redis", status: "healthy", latency: 1 },
  { name: "Neo4j", status: "healthy", latency: 8 },
  { name: "Qdrant", status: "healthy", latency: 5 },
  { name: "MinIO", status: "healthy", latency: 3 },
  { name: "Kafka", status: "degraded", latency: 45 },
];

const MOCK_AUDIT_LOG = [
  { timestamp: "2026-07-23T14:28:00Z", user: "system", action: "model_reload", resource: "Adaptive Ensemble", ip: "internal" },
  { timestamp: "2026-07-23T14:15:00Z", user: "analyst@aegisos.ai", action: "case_escalated", resource: "CASE-2026-0847", ip: "192.168.1.42" },
  { timestamp: "2026-07-23T13:50:00Z", user: "system", action: "threshold_update", resource: "risk_thresholds", ip: "internal" },
  { timestamp: "2026-07-23T12:30:00Z", user: "admin@aegisos.ai", action: "user_created", resource: "new_analyst_1", ip: "10.0.0.5" },
  { timestamp: "2026-07-23T11:00:00Z", user: "system", action: "drift_detected", resource: "XGBoost model", ip: "internal" },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<"thresholds" | "health" | "audit">("thresholds");
  const [thresholds, setThresholds] = useState({
    high: 0.6,
    very_high: 0.8,
    critical: 0.9,
    auto_block: 0.95,
  });

  const tabs = [
    { id: "thresholds" as const, label: "Risk Thresholds", icon: Shield },
    { id: "health" as const, label: "System Health", icon: Activity },
    { id: "audit" as const, label: "Audit Log", icon: Database },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <Settings className="h-7 w-7" />
          Settings
        </h1>
        <p className="text-muted-foreground">
          System configuration and administration
        </p>
      </div>

      <div className="flex gap-2 border-b pb-2">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            variant={activeTab === tab.id ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon className="h-4 w-4 mr-2" />
            {tab.label}
          </Button>
        ))}
      </div>

      {activeTab === "thresholds" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Risk Score Thresholds</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-sm text-muted-foreground">
              Configure the risk score boundaries that determine risk levels and automatic actions.
            </p>

            <div className="space-y-4">
              {Object.entries(thresholds).map(([key, value]) => (
                <div key={key} className="flex items-center gap-4">
                  <label className="text-sm font-medium w-32 capitalize">
                    {key.replace("_", " ")}
                  </label>
                  <Input
                    type="number"
                    min={0}
                    max={1}
                    step={0.05}
                    value={value}
                    onChange={(e) => setThresholds((prev) => ({ ...prev, [key]: parseFloat(e.target.value) }))}
                    className="w-24 font-mono"
                  />
                  <div className="flex-1 h-3 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono w-12 text-muted-foreground">
                    {(value * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>

            <Separator />

            <div className="flex items-center gap-3">
              <div className="flex-1 h-4 rounded-full overflow-hidden flex">
                <div className="bg-risk-very-low h-full" style={{ width: `${thresholds.high * 100}%` }} />
                <div className="bg-risk-medium h-full" style={{ width: `${(thresholds.very_high - thresholds.high) * 100}%` }} />
                <div className="bg-risk-high h-full" style={{ width: `${(thresholds.critical - thresholds.very_high) * 100}%` }} />
                <div className="bg-risk-very-high h-full" style={{ width: `${(thresholds.auto_block - thresholds.critical) * 100}%` }} />
                <div className="bg-risk-critical h-full" style={{ width: `${(1 - thresholds.auto_block) * 100}%` }} />
              </div>
            </div>

            <Button>Save Thresholds</Button>
          </CardContent>
        </Card>
      )}

      {activeTab === "health" && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {MOCK_SERVICES.map((service) => (
            <Card key={service.name}>
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Server className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{service.name}</p>
                    <p className="text-xs text-muted-foreground">{service.latency}ms latency</p>
                  </div>
                </div>
                {service.status === "healthy" ? (
                  <CheckCircle className="h-5 w-5 text-risk-very-low" />
                ) : (
                  <XCircle className="h-5 w-5 text-risk-medium" />
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {activeTab === "audit" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-2 text-left font-medium text-muted-foreground">Time</th>
                    <th className="px-4 py-2 text-left font-medium text-muted-foreground">User</th>
                    <th className="px-4 py-2 text-left font-medium text-muted-foreground">Action</th>
                    <th className="px-4 py-2 text-left font-medium text-muted-foreground">Resource</th>
                    <th className="px-4 py-2 text-left font-medium text-muted-foreground">IP</th>
                  </tr>
                </thead>
                <tbody>
                  {MOCK_AUDIT_LOG.map((entry, idx) => (
                    <tr key={idx} className="border-b">
                      <td className="px-4 py-2 text-xs font-mono">{new Date(entry.timestamp).toLocaleString()}</td>
                      <td className="px-4 py-2 text-xs">{entry.user}</td>
                      <td className="px-4 py-2">
                        <Badge variant="outline" className="text-xs">{entry.action}</Badge>
                      </td>
                      <td className="px-4 py-2 text-xs font-mono">{entry.resource}</td>
                      <td className="px-4 py-2 text-xs font-mono text-muted-foreground">{entry.ip}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
