"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchTransaction } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RiskBadge } from "@/components/shared/risk-badge";
import { formatCurrency, cn } from "@/lib/utils";
import {
  ArrowLeft,
  Shield,
  AlertTriangle,
  CheckCircle,
  Ban,
  Clock,
} from "lucide-react";

export default function TransactionDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: tx, isLoading } = useQuery({
    queryKey: ["transaction", id],
    queryFn: () => fetchTransaction(id),
  });

  if (isLoading || !tx) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const riskScore = tx.risk_score ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/transactions">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight font-mono">
            {tx.transaction_id}
          </h1>
          <p className="text-muted-foreground">Transaction Detail</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Transaction Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Type</p>
                  <p className="font-medium">{tx.type.replace("_", " ")}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Amount</p>
                  <p className="font-medium text-lg">{formatCurrency(tx.amount, tx.currency)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Sender</p>
                  <p className="font-mono text-xs">{tx.sender_id}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Receiver</p>
                  <p className="font-mono text-xs">{tx.receiver_id}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Channel</p>
                  <p className="font-medium capitalize">{tx.channel}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Country</p>
                  <p className="font-medium">{tx.country_code || "Unknown"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">IP Address</p>
                  <p className="font-mono text-xs">{tx.ip_address || "N/A"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Device</p>
                  <p className="font-mono text-xs">{tx.device_id || "N/A"}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Timestamp</p>
                  <p className="font-medium">{new Date(tx.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Processing Time</p>
                  <p className="font-medium">{tx.processing_time_ms}ms</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {tx.description && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-risk-medium" />
                  AI Explanation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed">{tx.description}</p>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col items-center gap-3">
                <div className="relative h-32 w-32">
                  <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
                    <circle
                      cx="50" cy="50" r="40"
                      fill="none"
                      stroke="hsl(var(--muted))"
                      strokeWidth="8"
                    />
                    <circle
                      cx="50" cy="50" r="40"
                      fill="none"
                      stroke={
                        riskScore > 0.8 ? "hsl(var(--risk-very-high))" :
                        riskScore > 0.5 ? "hsl(var(--risk-medium))" :
                        "hsl(var(--risk-very-low))"
                      }
                      strokeWidth="8"
                      strokeDasharray={`${riskScore * 251.2} 251.2`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold">
                      {(riskScore * 100).toFixed(0)}
                    </span>
                  </div>
                </div>
                {tx.risk_level && <RiskBadge level={tx.risk_level} />}
              </div>

              <div className="space-y-2 pt-2 border-t">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Verdict</span>
                  <Badge variant={tx.risk_verdict === "APPROVE" ? "success" : "destructive"}>
                    {tx.risk_verdict || "N/A"}
                  </Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Status</span>
                  <Badge variant="outline">{tx.status}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" variant="default" size="sm">
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve
              </Button>
              <Button className="w-full" variant="outline" size="sm">
                <Shield className="h-4 w-4 mr-2" />
                Send to Investigation
              </Button>
              <Button className="w-full" variant="destructive" size="sm">
                <Ban className="h-4 w-4 mr-2" />
                Block
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
