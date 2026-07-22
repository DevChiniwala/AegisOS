"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

function generateHeatmapData() {
  return DAYS.flatMap((day, dayIdx) =>
    HOURS.map((hour) => ({
      day: dayIdx,
      hour,
      value: Math.random() * 0.3 + (hour >= 1 && hour <= 5 ? 0.4 : 0) + (dayIdx >= 5 ? 0.1 : 0),
    }))
  );
}

function getHeatColor(value: number): string {
  if (value < 0.1) return "bg-risk-very-low/20";
  if (value < 0.2) return "bg-risk-low/30";
  if (value < 0.35) return "bg-risk-medium/40";
  if (value < 0.5) return "bg-risk-high/50";
  return "bg-risk-very-high/60";
}

export function RiskHeatmap() {
  const data = generateHeatmapData();

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium">
          Risk Heatmap (Time of Day × Day of Week)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <TooltipProvider>
          <div className="overflow-x-auto">
            <div className="min-w-[600px]">
              <div className="flex gap-0.5 mb-1 ml-10">
                {HOURS.filter((h) => h % 3 === 0).map((h) => (
                  <span
                    key={h}
                    className="text-[10px] text-muted-foreground"
                    style={{ width: `${100 / 8}%` }}
                  >
                    {h}:00
                  </span>
                ))}
              </div>
              {DAYS.map((day, dayIdx) => (
                <div key={day} className="flex items-center gap-1 mb-0.5">
                  <span className="text-xs text-muted-foreground w-8">
                    {day}
                  </span>
                  <div className="flex gap-0.5 flex-1">
                    {HOURS.map((hour) => {
                      const cell = data.find(
                        (d) => d.day === dayIdx && d.hour === hour
                      );
                      const value = cell?.value || 0;
                      return (
                        <Tooltip key={`${dayIdx}-${hour}`}>
                          <TooltipTrigger asChild>
                            <div
                              className={cn(
                                "h-5 flex-1 rounded-sm cursor-pointer transition-opacity hover:opacity-80",
                                getHeatColor(value)
                              )}
                            />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p className="text-xs">
                              {day} {hour}:00 — Risk: {(value * 100).toFixed(0)}%
                            </p>
                          </TooltipContent>
                        </Tooltip>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  );
}
