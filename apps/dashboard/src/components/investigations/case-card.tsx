"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RiskBadge } from "@/components/shared/risk-badge";
import { Clock, User } from "lucide-react";
import { cn } from "@/lib/utils";
import type { InvestigationCase } from "@/types/investigation";

interface CaseCardProps {
  case_: InvestigationCase;
}

const PRIORITY_COLOR: Record<string, string> = {
  CRITICAL: "border-l-risk-critical",
  HIGH: "border-l-risk-high",
  MEDIUM: "border-l-risk-medium",
  LOW: "border-l-risk-low",
};

const STATUS_VARIANT: Record<string, "default" | "secondary" | "warning" | "success" | "destructive"> = {
  OPEN: "secondary",
  TRIAGING: "secondary",
  INVESTIGATING: "default",
  EVIDENCE_REVIEW: "warning",
  DECIDED: "success",
  CLOSED: "success",
  ESCALATED: "destructive",
};

export function CaseCard({ case_ }: CaseCardProps) {
  const riskLevel =
    case_.risk_score >= 0.9 ? "CRITICAL" :
    case_.risk_score >= 0.7 ? "VERY_HIGH" :
    case_.risk_score >= 0.5 ? "HIGH" : "MEDIUM";

  return (
    <Link href={`/investigations/${case_.case_id}`}>
      <Card className={cn(
        "border-l-4 transition-all hover:shadow-md hover:bg-accent/30 cursor-pointer",
        PRIORITY_COLOR[case_.priority] || "border-l-border"
      )}>
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="font-mono text-sm font-semibold">{case_.case_id}</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {case_.findings.length} findings &middot; {case_.evidence.length} evidence items
              </p>
            </div>
            <Badge variant={STATUS_VARIANT[case_.status] || "secondary"} className="text-xs">
              {case_.status.replace("_", " ")}
            </Badge>
          </div>

          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-3">
              <RiskBadge level={riskLevel} />
              <span className="text-xs font-mono text-muted-foreground">
                {(case_.risk_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              {case_.assigned_to && (
                <span className="flex items-center gap-1">
                  <User className="h-3 w-3" />
                  {case_.assigned_to.replace("Agent: ", "")}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {new Date(case_.created_at).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
