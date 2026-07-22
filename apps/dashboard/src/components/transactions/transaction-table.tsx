"use client";

import { useRouter } from "next/navigation";
import { formatCurrency, cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { RiskBadge } from "@/components/shared/risk-badge";
import type { Transaction } from "@/types/transaction";

interface TransactionTableProps {
  transactions: Transaction[];
}

const STATUS_VARIANT: Record<string, "default" | "success" | "warning" | "danger" | "destructive" | "secondary"> = {
  APPROVED: "success",
  PENDING: "secondary",
  FLAGGED: "warning",
  UNDER_REVIEW: "warning",
  DECLINED: "danger",
  BLOCKED: "destructive",
};

export function TransactionTable({ transactions }: TransactionTableProps) {
  const router = useRouter();

  return (
    <div className="rounded-lg border">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">ID</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Type</th>
              <th className="px-4 py-3 text-right font-medium text-muted-foreground">Amount</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Sender</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Risk</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Score</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Time</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr
                key={tx.transaction_id}
                className="border-b cursor-pointer transition-colors hover:bg-accent/50"
                onClick={() => router.push(`/transactions/${tx.transaction_id}`)}
              >
                <td className="px-4 py-3 font-mono text-xs">
                  {tx.transaction_id.slice(0, 12)}
                </td>
                <td className="px-4 py-3">
                  <Badge variant="outline" className="text-xs">
                    {tx.type.replace("_", " ")}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right font-medium">
                  {formatCurrency(tx.amount, tx.currency)}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                  {tx.sender_id.slice(0, 10)}
                </td>
                <td className="px-4 py-3">
                  <Badge variant={STATUS_VARIANT[tx.status] || "secondary"} className="text-xs">
                    {tx.status.replace("_", " ")}
                  </Badge>
                </td>
                <td className="px-4 py-3">
                  {tx.risk_level && <RiskBadge level={tx.risk_level} />}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-16 rounded-full bg-muted overflow-hidden">
                      <div
                        className={cn(
                          "h-full rounded-full transition-all",
                          (tx.risk_score ?? 0) > 0.8 ? "bg-risk-very-high" :
                          (tx.risk_score ?? 0) > 0.5 ? "bg-risk-medium" :
                          "bg-risk-very-low"
                        )}
                        style={{ width: `${(tx.risk_score ?? 0) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono w-8">
                      {((tx.risk_score ?? 0) * 100).toFixed(0)}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-xs text-muted-foreground">
                  {new Date(tx.timestamp).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
