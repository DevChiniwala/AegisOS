"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchInvestigation } from "@/lib/api";
import { CaseTimeline } from "@/components/investigations/case-timeline";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { RiskBadge } from "@/components/shared/risk-badge";
import {
  ArrowLeft,
  FileWarning,
  Send,
  XCircle,
  CheckCircle,
} from "lucide-react";

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.caseId as string;

  const { data: case_, isLoading } = useQuery({
    queryKey: ["investigation", caseId],
    queryFn: () => fetchInvestigation(caseId),
  });

  if (isLoading || !case_) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const riskLevel =
    case_.risk_score >= 0.9 ? "CRITICAL" :
    case_.risk_score >= 0.7 ? "VERY_HIGH" :
    case_.risk_score >= 0.5 ? "HIGH" : "MEDIUM";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/investigations">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight font-mono">
              {case_.case_id}
            </h1>
            <Badge variant={case_.status === "INVESTIGATING" ? "default" : "secondary"}>
              {case_.status.replace("_", " ")}
            </Badge>
          </div>
          <p className="text-muted-foreground text-sm">
            Opened {new Date(case_.created_at).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">AI Agent Investigation Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px] pr-4">
                <CaseTimeline events={case_.timeline} />
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Case Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Risk Score</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold">
                    {(case_.risk_score * 100).toFixed(0)}%
                  </span>
                  <RiskBadge level={riskLevel} />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Priority</span>
                <Badge variant={case_.priority === "CRITICAL" ? "destructive" : "warning"}>
                  {case_.priority}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Transactions</span>
                <span className="text-sm font-medium">{case_.transaction_ids.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">SAR Filed</span>
                <span className="text-sm font-medium">
                  {case_.sar_generated ? "Yes" : "No"}
                </span>
              </div>
              {case_.verdict && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Verdict</span>
                  <Badge variant="destructive">{case_.verdict}</Badge>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">
                Findings ({case_.findings.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-3">
                  {case_.findings.map((f) => (
                    <div key={f.finding_id} className="rounded-md border p-3">
                      <div className="flex items-center justify-between mb-1">
                        <Badge variant="outline" className="text-xs">
                          {f.agent_name}
                        </Badge>
                        <span className="text-xs font-mono text-muted-foreground">
                          {(f.confidence * 100).toFixed(0)}% conf
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {f.description}
                      </p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" size="sm">
                <FileWarning className="h-4 w-4 mr-2" />
                Generate SAR Report
              </Button>
              <Button className="w-full" variant="outline" size="sm">
                <Send className="h-4 w-4 mr-2" />
                Escalate
              </Button>
              <Button className="w-full" variant="outline" size="sm">
                <CheckCircle className="h-4 w-4 mr-2" />
                Mark Resolved
              </Button>
              <Button className="w-full" variant="destructive" size="sm">
                <XCircle className="h-4 w-4 mr-2" />
                Close Case
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
