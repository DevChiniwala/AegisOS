import { apiClient } from "./client";
import { mockCases } from "@/lib/mock-data";
import type { InvestigationCase, TimelineEvent } from "@/types/investigation";

export async function fetchInvestigations(): Promise<InvestigationCase[]> {
  try {
    const { data } = await apiClient.get<InvestigationCase[]>("/investigations");
    return data;
  } catch {
    return mockCases;
  }
}

export async function fetchInvestigation(caseId: string): Promise<InvestigationCase> {
  try {
    const { data } = await apiClient.get<InvestigationCase>(`/investigations/${caseId}`);
    return data;
  } catch {
    const found = mockCases.find((c) => c.case_id === caseId);
    if (!found) throw new Error("Case not found");
    return found;
  }
}

export async function fetchInvestigationTimeline(caseId: string): Promise<TimelineEvent[]> {
  try {
    const { data } = await apiClient.get<TimelineEvent[]>(`/investigations/${caseId}/timeline`);
    return data;
  } catch {
    const found = mockCases.find((c) => c.case_id === caseId);
    return found?.timeline || [];
  }
}
