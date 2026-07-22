import type { DashboardOverview, TimelineDataPoint, TopRisk, ModelPerformance } from "@/types/api";

export const mockOverview: DashboardOverview = {
  total_transactions: 284731,
  fraud_rate: 0.0147,
  avg_score: 0.052,
  alerts_today: 47,
  transactions_change: 12.3,
  fraud_rate_change: -2.1,
  alerts_change: 8.5,
};

export const mockTimeline: TimelineDataPoint[] = Array.from({ length: 24 }, (_, i) => ({
  timestamp: `2026-07-23T${String(i).padStart(2, "0")}:00:00Z`,
  transactions: Math.floor(8000 + Math.random() * 4000),
  fraud_count: Math.floor(5 + Math.random() * 20),
  avg_risk: 0.03 + Math.random() * 0.04,
}));

export const mockTopRisks: TopRisk[] = [
  { entity_id: "usr_8d2f1", entity_type: "user", name: "Viktor Petrov", risk_score: 0.94, reason: "Velocity spike: 23 transactions in 4 minutes across 5 countries" },
  { entity_id: "usr_3a9c2", entity_type: "user", name: "Maria Santos", risk_score: 0.89, reason: "New device + high-value wire transfer to sanctioned jurisdiction" },
  { entity_id: "mrc_f721a", entity_type: "merchant", name: "QuickSwap Crypto Exchange", risk_score: 0.87, reason: "Detected as money mule relay node in graph analysis" },
  { entity_id: "usr_1e5d4", entity_type: "user", name: "James Chen", risk_score: 0.82, reason: "Account takeover indicators: password reset + device change + immediate transfer" },
  { entity_id: "usr_7b4e3", entity_type: "user", name: "Anonymous KYC", risk_score: 0.79, reason: "Synthetic identity detected: SSN/DOB mismatch, no credit history" },
];

export const mockModelPerformance: ModelPerformance[] = [
  { model_name: "Adaptive Ensemble", accuracy: 0.994, precision: 0.89, recall: 0.84, f1: 0.86, auc: 0.97, latency_p50: 8, latency_p95: 18, latency_p99: 42 },
  { model_name: "XGBoost", accuracy: 0.992, precision: 0.86, recall: 0.81, f1: 0.83, auc: 0.96, latency_p50: 3, latency_p95: 7, latency_p99: 15 },
  { model_name: "LightGBM", accuracy: 0.991, precision: 0.84, recall: 0.82, f1: 0.83, auc: 0.95, latency_p50: 2, latency_p95: 5, latency_p99: 11 },
  { model_name: "CatBoost", accuracy: 0.993, precision: 0.87, recall: 0.80, f1: 0.83, auc: 0.96, latency_p50: 4, latency_p95: 9, latency_p99: 22 },
  { model_name: "Isolation Forest", accuracy: 0.985, precision: 0.72, recall: 0.88, f1: 0.79, auc: 0.93, latency_p50: 1, latency_p95: 3, latency_p99: 8 },
];
