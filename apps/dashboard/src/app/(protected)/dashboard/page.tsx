"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchOverview, fetchTimeline, fetchTopRisks, fetchModelPerformance } from "@/lib/api";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { TimelineChart } from "@/components/dashboard/timeline-chart";
import { AlertFeed } from "@/components/dashboard/alert-feed";
import { RiskHeatmap } from "@/components/dashboard/risk-heatmap";
import { ModelSummary } from "@/components/dashboard/model-summary";
import { ArrowLeftRight, ShieldAlert, Activity, Gauge } from "lucide-react";
import { formatNumber, formatPercentage } from "@/lib/utils";

export default function DashboardPage() {
  const { data: overview } = useQuery({
    queryKey: ["dashboard-overview"],
    queryFn: fetchOverview,
    refetchInterval: 30000,
  });

  const { data: timeline } = useQuery({
    queryKey: ["dashboard-timeline"],
    queryFn: fetchTimeline,
    refetchInterval: 30000,
  });

  const { data: topRisks } = useQuery({
    queryKey: ["dashboard-top-risks"],
    queryFn: fetchTopRisks,
  });

  const { data: models } = useQuery({
    queryKey: ["dashboard-models"],
    queryFn: fetchModelPerformance,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time fraud intelligence overview
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Total Transactions"
          value={overview?.total_transactions ?? 0}
          change={overview?.transactions_change}
          icon={ArrowLeftRight}
          formatFn={formatNumber}
        />
        <KpiCard
          title="Fraud Rate"
          value={(overview?.fraud_rate ?? 0) * 10000}
          change={overview?.fraud_rate_change}
          icon={ShieldAlert}
          formatFn={(v) => formatPercentage(v / 10000)}
        />
        <KpiCard
          title="Alerts Today"
          value={overview?.alerts_today ?? 0}
          change={overview?.alerts_change}
          icon={Activity}
        />
        <KpiCard
          title="Avg Risk Score"
          value={(overview?.avg_score ?? 0) * 100}
          icon={Gauge}
          formatFn={(v) => `${v.toFixed(1)}%`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <TimelineChart data={timeline ?? []} />
        </div>
        <AlertFeed alerts={topRisks ?? []} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <RiskHeatmap />
        <ModelSummary models={models ?? []} />
      </div>
    </div>
  );
}
