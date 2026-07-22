"use client";

import { cn } from "@/lib/utils";

interface ConnectionStatusProps {
  status: "connecting" | "connected" | "disconnected" | "reconnecting";
}

const STATUS_CONFIG = {
  connected: { color: "bg-risk-very-low", label: "Connected", pulse: false },
  connecting: { color: "bg-risk-medium", label: "Connecting...", pulse: true },
  reconnecting: { color: "bg-risk-medium", label: "Reconnecting...", pulse: true },
  disconnected: { color: "bg-risk-very-high", label: "Disconnected", pulse: false },
};

export function ConnectionStatus({ status }: ConnectionStatusProps) {
  const config = STATUS_CONFIG[status];

  return (
    <div className="flex items-center gap-2">
      <div className="relative flex h-3 w-3">
        {config.pulse && (
          <span className={cn("absolute inline-flex h-full w-full animate-ping rounded-full opacity-75", config.color)} />
        )}
        <span className={cn("relative inline-flex h-3 w-3 rounded-full", config.color)} />
      </div>
      <span className="text-xs text-muted-foreground">{config.label}</span>
    </div>
  );
}
