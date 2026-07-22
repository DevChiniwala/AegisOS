"use client";

import { cn, formatCurrency } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { RiskBadge } from "@/components/shared/risk-badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { motion, AnimatePresence } from "framer-motion";
import type { Transaction } from "@/types/transaction";

interface LiveFeedProps {
  transactions: Transaction[];
  paused: boolean;
}

export function LiveFeed({ transactions, paused }: LiveFeedProps) {
  return (
    <ScrollArea className="h-[600px]">
      <AnimatePresence initial={false}>
        {transactions.map((tx, idx) => {
          const isHighRisk = (tx.risk_score ?? 0) >= 0.7;
          return (
            <motion.div
              key={tx.transaction_id + idx}
              initial={{ opacity: 0, x: -20, height: 0 }}
              animate={{ opacity: 1, x: 0, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className={cn(
                "border-b px-4 py-3 transition-colors",
                isHighRisk && "border-l-2 border-l-risk-very-high bg-risk-very-high/5",
                isHighRisk && !paused && "animate-pulse-risk"
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex flex-col">
                    <span className="font-mono text-xs text-muted-foreground">
                      {tx.transaction_id.slice(0, 12)}
                    </span>
                    <span className="text-sm font-medium">
                      {formatCurrency(tx.amount, tx.currency)}
                    </span>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {tx.type.replace("_", " ")}
                  </Badge>
                </div>
                <div className="flex items-center gap-3">
                  {tx.risk_level && <RiskBadge level={tx.risk_level} />}
                  <span className="text-xs text-muted-foreground font-mono">
                    {new Date(tx.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                <span>{tx.sender_id.slice(0, 8)}</span>
                <span>→</span>
                <span>{tx.receiver_id.slice(0, 8)}</span>
                {tx.country_code && (
                  <Badge variant="outline" className="text-[10px] ml-auto">
                    {tx.country_code}
                  </Badge>
                )}
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </ScrollArea>
  );
}
