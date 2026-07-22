import axios, { type AxiosInstance, type AxiosError } from "axios";
import { API_BASE_URL } from "@/lib/constants";

const TOKEN_KEY = "aegis_token";

function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    timeout: 15000,
    headers: { "Content-Type": "application/json" },
  });

  client.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response?.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem("aegis_user");
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }
  );

  return client;
}

export const apiClient = createApiClient();
