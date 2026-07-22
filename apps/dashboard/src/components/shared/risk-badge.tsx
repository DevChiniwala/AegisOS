import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface RiskBadgeProps {
  level: string;
  className?: string;
}

const RISK_STYLES: Record<string, { variant: "success" | "warning" | "danger" | "destructive" | "secondary"; label: string }> = {
  VERY_LOW: { variant: "success", label: "Very Low" },
  LOW: { variant: "success", label: "Low" },
  MEDIUM: { variant: "warning", label: "Medium" },
  HIGH: { variant: "danger", label: "High" },
  VERY_HIGH: { variant: "destructive", label: "Very High" },
  CRITICAL: { variant: "destructive", label: "Critical" },
};

export function RiskBadge({ level, className }: RiskBadgeProps) {
  const style = RISK_STYLES[level] || { variant: "secondary" as const, label: level };
  return (
    <Badge variant={style.variant} className={cn(className)}>
      {style.label}
    </Badge>
  );
}
