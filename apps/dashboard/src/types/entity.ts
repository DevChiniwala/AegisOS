export interface UserProfile {
  user_id: string;
  name: string;
  email?: string;
  phone?: string;
  date_of_birth?: string;
  kyc_status: "verified" | "pending" | "rejected" | "not_started";
  kyc_verified_at?: string;
  risk_tier: "low" | "medium" | "high";
  account_age_days: number;
  country: string;
  created_at: string;
}

export interface MerchantProfile {
  merchant_id: string;
  name: string;
  category: string;
  mcc_code: string;
  risk_tier: "low" | "medium" | "high";
  country: string;
  registration_date: string;
  is_verified: boolean;
}

export interface DeviceFingerprint {
  device_id: string;
  user_id: string;
  device_type: string;
  os: string;
  browser?: string;
  screen_resolution?: string;
  language?: string;
  timezone?: string;
  is_emulator: boolean;
  is_rooted: boolean;
  first_seen: string;
  last_seen: string;
}
