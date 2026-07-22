export interface DashboardOverview {
  total_transactions: number;
  fraud_rate: number;
  avg_score: number;
  alerts_today: number;
  transactions_change: number;
  fraud_rate_change: number;
  alerts_change: number;
}

export interface TimelineDataPoint {
  timestamp: string;
  transactions: number;
  fraud_count: number;
  avg_risk: number;
}

export interface ModelPerformance {
  model_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  auc: number;
  latency_p50: number;
  latency_p95: number;
  latency_p99: number;
}

export interface SystemHealth {
  status: "healthy" | "degraded" | "unhealthy";
  services: Record<string, { status: string; latency_ms: number }>;
  uptime_seconds: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TopRisk {
  entity_id: string;
  entity_type: string;
  name: string;
  risk_score: number;
  reason: string;
}
