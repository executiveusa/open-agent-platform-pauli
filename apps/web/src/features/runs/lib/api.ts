import type { RunDetail, RunSummary } from "@/types/run";

const API_BASE = process.env.NEXT_PUBLIC_RUNS_API ?? "http://localhost:8000";

export async function listRuns(): Promise<RunSummary[]> {
  const response = await fetch(`${API_BASE}/api/runs`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load runs");
  }
  const data = (await response.json()) as { items: RunSummary[] };
  return data.items;
}

export async function getRun(runId: string): Promise<RunDetail> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load run");
  }
  return (await response.json()) as RunDetail;
}

export async function getRunSession(runId: string): Promise<{
  url: string;
  token: string;
  expires_at: string;
}> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/session`, {
    method: "GET",
  });
  if (!response.ok) {
    throw new Error("Failed to load session");
  }
  return (await response.json()) as {
    url: string;
    token: string;
    expires_at: string;
  };
}
