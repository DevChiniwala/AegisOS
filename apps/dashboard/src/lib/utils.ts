import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
}

export function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toLocaleString();
}

export function formatPercentage(value: number, decimals = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function getRiskColor(score: number): string {
  if (score <= 0.2) return "text-risk-very-low";
  if (score <= 0.4) return "text-risk-low";
  if (score <= 0.6) return "text-risk-medium";
  if (score <= 0.8) return "text-risk-high";
  if (score <= 0.9) return "text-risk-very-high";
  return "text-risk-critical";
}

export function getRiskBgColor(score: number): string {
  if (score <= 0.2) return "bg-risk-very-low";
  if (score <= 0.4) return "bg-risk-low";
  if (score <= 0.6) return "bg-risk-medium";
  if (score <= 0.8) return "bg-risk-high";
  if (score <= 0.9) return "bg-risk-very-high";
  return "bg-risk-critical";
}
