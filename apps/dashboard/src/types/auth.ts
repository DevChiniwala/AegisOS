export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "analyst" | "viewer" | "api_user";
  avatar?: string;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
