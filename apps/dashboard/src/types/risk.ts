export enum RiskLevel {
  VERY_LOW = "VERY_LOW",
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  VERY_HIGH = "VERY_HIGH",
  CRITICAL = "CRITICAL",
}

export enum RiskVerdict {
  APPROVE = "APPROVE",
  REVIEW = "REVIEW",
  DECLINE = "DECLINE",
  BLOCK = "BLOCK",
}

export interface RiskScore {
  score: number;
  level: RiskLevel;
  verdict: RiskVerdict;
  confidence: number;
  model_version: string;
  scored_at: string;
}

export interface FeatureImportance {
  feature_name: string;
  value: number | string;
  importance: number;
  direction: "increases_risk" | "decreases_risk";
}

export interface RiskExplanation {
  risk_score: RiskScore;
  top_features: FeatureImportance[];
  shap_values: Record<string, number>;
  graph_evidence: Array<Record<string, unknown>>;
  behavioral_deviations: string[];
  counterfactual: string;
  natural_language_explanation: string;
  similar_cases: Array<Record<string, unknown>>;
  rules_triggered: string[];
}

export interface RiskThresholds {
  high: number;
  very_high: number;
  critical: number;
  auto_block: number;
}

export interface RiskHeatmapCell {
  hour: number;
  day: number;
  value: number;
}
