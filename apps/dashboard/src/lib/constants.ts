import {
  LayoutDashboard,
  ArrowLeftRight,
  Search,
  Network,
  Radio,
  Activity,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Transactions", href: "/transactions", icon: ArrowLeftRight },
  { title: "Investigations", href: "/investigations", icon: Search },
  { title: "Graph Explorer", href: "/graph", icon: Network },
  { title: "Live Feed", href: "/live", icon: Radio },
  { title: "Models", href: "/models", icon: Activity },
  { title: "Settings", href: "/settings", icon: Settings },
];

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || "AegisOS";
