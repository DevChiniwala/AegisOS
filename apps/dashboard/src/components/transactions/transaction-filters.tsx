"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Search, X } from "lucide-react";
import { TransactionStatus, TransactionType } from "@/types/transaction";

interface TransactionFiltersProps {
  filters: {
    search: string;
    status: string[];
    riskLevel: string[];
    type: string[];
  };
  onFilterChange: (key: string, value: unknown) => void;
  onReset: () => void;
}

const RISK_LEVELS = ["VERY_LOW", "LOW", "MEDIUM", "HIGH", "VERY_HIGH", "CRITICAL"];

export function TransactionFilters({ filters, onFilterChange, onReset }: TransactionFiltersProps) {
  const toggleArrayFilter = (key: string, value: string) => {
    const current = filters[key as keyof typeof filters] as string[];
    const updated = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    onFilterChange(key, updated);
  };

  const hasFilters = filters.search || filters.status.length > 0 || filters.riskLevel.length > 0 || filters.type.length > 0;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by ID, sender, or merchant..."
            className="pl-9"
            value={filters.search}
            onChange={(e) => onFilterChange("search", e.target.value)}
          />
        </div>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={onReset}>
            <X className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      <div className="flex flex-wrap gap-4">
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground font-medium">Status</p>
          <div className="flex flex-wrap gap-1">
            {Object.values(TransactionStatus).map((status) => (
              <Badge
                key={status}
                variant={filters.status.includes(status) ? "default" : "outline"}
                className="cursor-pointer text-xs"
                onClick={() => toggleArrayFilter("status", status)}
              >
                {status.replace("_", " ")}
              </Badge>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          <p className="text-xs text-muted-foreground font-medium">Risk Level</p>
          <div className="flex flex-wrap gap-1">
            {RISK_LEVELS.map((level) => (
              <Badge
                key={level}
                variant={filters.riskLevel.includes(level) ? "default" : "outline"}
                className="cursor-pointer text-xs"
                onClick={() => toggleArrayFilter("riskLevel", level)}
              >
                {level.replace("_", " ")}
              </Badge>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          <p className="text-xs text-muted-foreground font-medium">Type</p>
          <div className="flex flex-wrap gap-1">
            {Object.values(TransactionType).map((type) => (
              <Badge
                key={type}
                variant={filters.type.includes(type) ? "default" : "outline"}
                className="cursor-pointer text-xs"
                onClick={() => toggleArrayFilter("type", type)}
              >
                {type.replace("_", " ")}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
