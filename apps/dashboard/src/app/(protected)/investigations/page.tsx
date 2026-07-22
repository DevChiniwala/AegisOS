"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchInvestigations } from "@/lib/api";
import { CaseCard } from "@/components/investigations/case-card";

export default function InvestigationsPage() {
  const { data: cases } = useQuery({
    queryKey: ["investigations"],
    queryFn: fetchInvestigations,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Investigations</h1>
        <p className="text-muted-foreground">
          AI-driven fraud investigation cases
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {(cases ?? []).map((c) => (
          <CaseCard key={c.case_id} case_={c} />
        ))}
      </div>
    </div>
  );
}
