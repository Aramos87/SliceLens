import type { FaqItem, ResidualResponse, RunSummary, SearchResponse } from "./types";

async function getJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`${response.status} ${url}`);
  }
  return response.json() as Promise<T>;
}

export function listRuns(): Promise<{ runs: RunSummary[] }> {
  return getJson("/api/runs");
}

export function searchRun(runId: string): Promise<SearchResponse> {
  return getJson(`/api/runs/${runId}/search`, { method: "POST" });
}

export function residualSearch(runId: string, memberIds: string[]): Promise<ResidualResponse> {
  return getJson(`/api/runs/${runId}/residual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ member_ids: memberIds }),
  });
}

export function loadFaq(): Promise<{ items: FaqItem[] }> {
  return getJson("/api/faq");
}
