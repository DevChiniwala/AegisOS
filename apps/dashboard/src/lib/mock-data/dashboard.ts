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
  { model_name: "SGAE (Dynamic Ensemble)", accuracy: 0.999, precision: 0.892, recall: 0.914, f1: 0.903, auc: 0.998, latency_p50: 42, latency_p95: 48, latency_p99: 55 },
  { model_name: "XGBoost (Deep Core)", accuracy: 0.998, precision: 0.017, recall: 0.994, f1: 0.034, auc: 0.998, latency_p50: 0.03, latency_p95: 0.05, latency_p99: 0.08 },
  { model_name: "LightGBM (Fast Path)", accuracy: 0.996, precision: 0.019, recall: 0.988, f1: 0.038, auc: 0.996, latency_p50: 0.04, latency_p95: 0.06, latency_p99: 0.1 },
  { model_name: "CatBoost (Categorical)", accuracy: 0.997, precision: 0.018, recall: 0.994, f1: 0.035, auc: 0.997, latency_p50: 0.03, latency_p95: 0.06, latency_p99: 0.09 },
  { model_name: "Temporal Graph Network", accuracy: 0.988, precision: 0.812, recall: 0.880, f1: 0.845, auc: 0.965, latency_p50: 28, latency_p95: 35, latency_p99: 45 },
];
