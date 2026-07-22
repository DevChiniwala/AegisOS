export enum TransactionType {
  CREDIT_CARD = "CREDIT_CARD",
  DEBIT_CARD = "DEBIT_CARD",
  UPI = "UPI",
  WIRE_TRANSFER = "WIRE_TRANSFER",
  ACH = "ACH",
  CRYPTO = "CRYPTO",
  P2P = "P2P",
}

export enum TransactionStatus {
  PENDING = "PENDING",
  APPROVED = "APPROVED",
  DECLINED = "DECLINED",
  FLAGGED = "FLAGGED",
  BLOCKED = "BLOCKED",
  UNDER_REVIEW = "UNDER_REVIEW",
}

export interface Transaction {
  transaction_id: string;
  type: TransactionType;
  amount: number;
  currency: string;
  timestamp: string;
  sender_id: string;
  receiver_id: string;
  sender_account?: string;
  receiver_account?: string;
  merchant_id?: string;
  channel: string;
  ip_address?: string;
  device_id?: string;
  geo_lat?: number;
  geo_lon?: number;
  country_code?: string;
  description?: string;
  metadata?: Record<string, unknown>;
  risk_score?: number;
  risk_level?: string;
  risk_verdict?: string;
  status: TransactionStatus;
  processing_time_ms?: number;
}
