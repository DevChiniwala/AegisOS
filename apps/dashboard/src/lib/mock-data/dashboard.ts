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

export const mockTimeline: TimelineDataPoint[] = [
  { timestamp: "2026-07-23T00:00:00Z", transactions: 9200, fraud_count: 12, avg_risk: 0.031 },
  { timestamp: "2026-07-23T01:00:00Z", transactions: 7800, fraud_count: 8, avg_risk: 0.029 },
  { timestamp: "2026-07-23T02:00:00Z", transactions: 6100, fraud_count: 5, avg_risk: 0.025 },
  { timestamp: "2026-07-23T03:00:00Z", transactions: 4500, fraud_count: 4, avg_risk: 0.022 },
  { timestamp: "2026-07-23T04:00:00Z", transactions: 4200, fraud_count: 3, avg_risk: 0.021 },
  { timestamp: "2026-07-23T05:00:00Z", transactions: 5100, fraud_count: 6, avg_risk: 0.024 },
  { timestamp: "2026-07-23T06:00:00Z", transactions: 8400, fraud_count: 15, avg_risk: 0.035 },
  { timestamp: "2026-07-23T07:00:00Z", transactions: 11200, fraud_count: 22, avg_risk: 0.042 },
  { timestamp: "2026-07-23T08:00:00Z", transactions: 13500, fraud_count: 28, avg_risk: 0.045 },
  { timestamp: "2026-07-23T09:00:00Z", transactions: 14200, fraud_count: 31, avg_risk: 0.048 },
  { timestamp: "2026-07-23T10:00:00Z", transactions: 13800, fraud_count: 29, avg_risk: 0.046 },
  { timestamp: "2026-07-23T11:00:00Z", transactions: 14100, fraud_count: 32, avg_risk: 0.049 },
  { timestamp: "2026-07-23T12:00:00Z", transactions: 15200, fraud_count: 145, avg_risk: 0.120 }, // Simulated Fraud Attack
  { timestamp: "2026-07-23T13:00:00Z", transactions: 15600, fraud_count: 180, avg_risk: 0.145 },
  { timestamp: "2026-07-23T14:00:00Z", transactions: 14900, fraud_count: 45, avg_risk: 0.055 },
  { timestamp: "2026-07-23T15:00:00Z", transactions: 14200, fraud_count: 31, avg_risk: 0.047 },
  { timestamp: "2026-07-23T16:00:00Z", transactions: 13900, fraud_count: 28, avg_risk: 0.045 },
  { timestamp: "2026-07-23T17:00:00Z", transactions: 15100, fraud_count: 35, avg_risk: 0.051 },
  { timestamp: "2026-07-23T18:00:00Z", transactions: 16800, fraud_count: 42, avg_risk: 0.058 },
  { timestamp: "2026-07-23T19:00:00Z", transactions: 17200, fraud_count: 44, avg_risk: 0.061 },
  { timestamp: "2026-07-23T20:00:00Z", transactions: 15500, fraud_count: 38, avg_risk: 0.054 },
  { timestamp: "2026-07-23T21:00:00Z", transactions: 13200, fraud_count: 25, avg_risk: 0.042 },
  { timestamp: "2026-07-23T22:00:00Z", transactions: 11400, fraud_count: 18, avg_risk: 0.038 },
  { timestamp: "2026-07-23T23:00:00Z", transactions: 9800, fraud_count: 14, avg_risk: 0.034 },
];

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
