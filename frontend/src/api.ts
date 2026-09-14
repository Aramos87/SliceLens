import type {
  DemoPack,
  FaqItem,
  Guide,
  ResidualResponse,
  RunSummary,
  SearchResponse,
} from "./types";

async function getJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    let detail = `${response.status} ${url}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* keep fallback */
    }
    throw new Error(detail);
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

export function loadGuide(runId: string): Promise<{ run: RunSummary; guide: Guide }> {
  return getJson(`/api/runs/${runId}/examples`);
}

export function loadPack(runId: string): Promise<DemoPack> {
  return getJson(`/api/runs/${runId}/pack`);
}

export function analyzePack(pack: DemoPack): Promise<SearchResponse> {
  return getJson("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(pack),
  });
}

export function analyzeResidual(pack: DemoPack, memberIds: string[]): Promise<ResidualResponse> {
  return getJson("/api/analyze/residual", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      member_ids: memberIds,
      items: pack.items,
      title: pack.title,
      id: pack.id,
      blurb: pack.blurb,
    }),
  });
}

export function loadFaq(): Promise<{ items: FaqItem[] }> {
  return getJson("/api/faq");
}
