"use client";

import { useState, useEffect, useCallback } from "react";
import type { User, AuthState, LoginCredentials, AuthTokens } from "@/types/auth";
import { API_BASE_URL } from "@/lib/constants";

const TOKEN_KEY = "aegis_token";
const USER_KEY = "aegis_user";

export function useAuth(): AuthState & {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
} {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    const userStr = localStorage.getItem(USER_KEY);
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr) as User;
        setState({ user, token, isAuthenticated: true, isLoading: false });
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setState((s) => ({ ...s, isLoading: false }));
      }
    } else {
      setState((s) => ({ ...s, isLoading: false }));
    }
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    if (!res.ok) {
      throw new Error("Invalid credentials");
    }

    const tokens: AuthTokens = await res.json();
    localStorage.setItem(TOKEN_KEY, tokens.access_token);

    const userRes = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${tokens.access_token}` },
    });

    let user: User;
    if (userRes.ok) {
      user = await userRes.json();
    } else {
      user = {
        id: "1",
        email: credentials.email,
        name: credentials.email.split("@")[0],
        role: "analyst",
        created_at: new Date().toISOString(),
      };
    }

    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setState({ user, token: tokens.access_token, isAuthenticated: true, isLoading: false });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setState({ user: null, token: null, isAuthenticated: false, isLoading: false });
  }, []);

  return { ...state, login, logout };
}
