import { apiClient } from "./client";
import { mockGraphData, mockCommunities } from "@/lib/mock-data";
import type { GraphData, Community } from "@/types/graph";

export async function fetchEntityGraph(entityId: string): Promise<GraphData> {
  try {
    const { data } = await apiClient.get<GraphData>(`/graph/entity/${entityId}`);
    return data;
  } catch {
    return mockGraphData;
  }
}

export async function fetchCommunities(): Promise<Community[]> {
  try {
    const { data } = await apiClient.get<Community[]>("/graph/communities");
    return data;
  } catch {
    return mockCommunities;
  }
}

export async function fetchGraphPath(
  sourceId: string,
  targetId: string
): Promise<GraphData> {
  try {
    const { data } = await apiClient.get<GraphData>(`/graph/path/${sourceId}/${targetId}`);
    return data;
  } catch {
    return mockGraphData;
  }
}
