import { apiClient } from "./client";
import { mockOverview, mockTimeline, mockTopRisks, mockModelPerformance } from "@/lib/mock-data";
import type { DashboardOverview, TimelineDataPoint, TopRisk, ModelPerformance } from "@/types/api";

export async function fetchOverview(): Promise<DashboardOverview> {
  try {
    const { data } = await apiClient.get<DashboardOverview>("/dashboard/overview");
    return data;
  } catch {
    return mockOverview;
  }
}

export async function fetchTimeline(): Promise<TimelineDataPoint[]> {
  try {
    const { data } = await apiClient.get<{ data: TimelineDataPoint[] }>("/dashboard/timeline");
    return data.data;
  } catch {
    return mockTimeline;
  }
}

export async function fetchTopRisks(): Promise<TopRisk[]> {
  try {
    const { data } = await apiClient.get<TopRisk[]>("/dashboard/top-risks");
    return data;
  } catch {
    return mockTopRisks;
  }
}

export async function fetchModelPerformance(): Promise<ModelPerformance[]> {
  try {
    const { data } = await apiClient.get<ModelPerformance[]>("/dashboard/model-performance");
    return Array.isArray(data) ? data : mockModelPerformance;
  } catch {
    return mockModelPerformance;
  }
}
