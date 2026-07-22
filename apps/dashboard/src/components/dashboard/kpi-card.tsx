"use client";

import { Card, CardContent } from "@/components/ui/card";
import { AnimatedCounter } from "@/components/shared/animated-counter";
import { TrendingUp, TrendingDown, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  title: string;
  value: number;
  change?: number;
  icon: LucideIcon;
  formatFn?: (value: number) => string;
  className?: string;
}

export function KpiCard({
  title,
  value,
  change,
  icon: Icon,
  formatFn,
  className,
}: KpiCardProps) {
  const isPositive = change !== undefined && change >= 0;

  return (
    <Card className={cn("relative overflow-hidden", className)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <div className="text-2xl font-bold">
              <AnimatedCounter value={value} formatFn={formatFn} />
            </div>
          </div>
          <div className="rounded-full bg-primary/10 p-3">
            <Icon className="h-5 w-5 text-primary" />
          </div>
        </div>
        {change !== undefined && (
          <div className="mt-3 flex items-center gap-1 text-xs">
            {isPositive ? (
              <TrendingUp className="h-3 w-3 text-risk-very-low" />
            ) : (
              <TrendingDown className="h-3 w-3 text-risk-very-high" />
            )}
            <span
              className={cn(
                "font-medium",
                isPositive ? "text-risk-very-low" : "text-risk-very-high"
              )}
            >
              {isPositive ? "+" : ""}
              {change.toFixed(1)}%
            </span>
            <span className="text-muted-foreground">vs last 24h</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
