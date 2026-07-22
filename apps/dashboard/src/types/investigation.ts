export enum CaseStatus {
  OPEN = "OPEN",
  TRIAGING = "TRIAGING",
  INVESTIGATING = "INVESTIGATING",
  EVIDENCE_REVIEW = "EVIDENCE_REVIEW",
  DECIDED = "DECIDED",
  CLOSED = "CLOSED",
  ESCALATED = "ESCALATED",
}

export enum CasePriority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export interface Finding {
  finding_id: string;
  agent_name: string;
  finding_type: string;
  description: string;
  confidence: number;
  evidence_refs: string[];
  timestamp: string;
}

export interface Evidence {
  evidence_id: string;
  type: string;
  source: string;
  content: string;
  metadata: Record<string, unknown>;
  timestamp: string;
}

export interface TimelineEvent {
  event_id: string;
  timestamp: string;
  event_type: string;
  description: string;
  agent_name: string;
  data?: Record<string, unknown>;
}

export interface InvestigationCase {
  case_id: string;
  transaction_ids: string[];
  entity_ids: string[];
  status: CaseStatus;
  priority: CasePriority;
  risk_score: number;
  assigned_to?: string;
  findings: Finding[];
  evidence: Evidence[];
  timeline: TimelineEvent[];
  created_at: string;
  updated_at: string;
  closed_at?: string;
  verdict?: string;
  sar_generated: boolean;
}
