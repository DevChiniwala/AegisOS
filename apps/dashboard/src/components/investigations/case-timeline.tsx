"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  Bot,
  Search,
  Network,
  Brain,
  Shield,
  FileText,
  Gavel,
  Eye,
  AlertCircle,
} from "lucide-react";
import type { TimelineEvent } from "@/types/investigation";

interface CaseTimelineProps {
  events: TimelineEvent[];
}

const AGENT_ICONS: Record<string, typeof Bot> = {
  System: AlertCircle,
  Supervisor: Eye,
  "Transaction Investigator": Search,
  "Graph Detective": Network,
  "Behavior Analyst": Brain,
  "Risk Assessor": Shield,
  "Compliance Officer": FileText,
  "Decision Agent": Gavel,
};

const AGENT_COLORS: Record<string, string> = {
  System: "bg-muted text-muted-foreground",
  Supervisor: "bg-purple-500/20 text-purple-400",
  "Transaction Investigator": "bg-blue-500/20 text-blue-400",
  "Graph Detective": "bg-emerald-500/20 text-emerald-400",
  "Behavior Analyst": "bg-orange-500/20 text-orange-400",
  "Risk Assessor": "bg-red-500/20 text-red-400",
  "Compliance Officer": "bg-yellow-500/20 text-yellow-400",
  "Decision Agent": "bg-pink-500/20 text-pink-400",
};

export function CaseTimeline({ events }: CaseTimelineProps) {
  return (
    <div className="relative space-y-0">
      <div className="absolute left-5 top-0 bottom-0 w-px bg-border" />

      {events.map((event, idx) => {
        const Icon = AGENT_ICONS[event.agent_name] || Bot;
        const colorClass = AGENT_COLORS[event.agent_name] || "bg-muted text-muted-foreground";

        return (
          <div key={event.event_id} className="relative flex gap-4 pb-6">
            <div className={cn("relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full", colorClass)}>
              <Icon className="h-4 w-4" />
            </div>
            <div className="flex-1 pt-1">
              <div className="flex items-center gap-2 mb-1">
                <Badge variant="outline" className="text-xs">
                  {event.agent_name}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-sm">{event.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
