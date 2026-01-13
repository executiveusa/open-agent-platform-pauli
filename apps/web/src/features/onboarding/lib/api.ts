const API_BASE = process.env.NEXT_PUBLIC_RUNS_API ?? "http://localhost:8000";

export async function fetchOnboardingTemplate() {
  const response = await fetch(`${API_BASE}/api/onboarding/template`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to load template");
  }
  return response.json() as Promise<{
    id: string;
    min_stage_fields: string[];
    stages: {
      id: string;
      questions: {
        id: string;
        type: string;
        required: boolean;
        choices?: string[];
        prompt: Record<string, string>;
      }[];
    }[];
  }>;
}

export async function startOnboardingSession(payload: {
  locale: string;
  persona?: Record<string, string>;
  orgName?: string;
}) {
  const response = await fetch(`${API_BASE}/api/onboarding/session/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      locale: payload.locale,
      persona: payload.persona ?? {},
      org_name: payload.orgName,
    }),
  });
  if (!response.ok) {
    throw new Error("Failed to start session");
  }
  return response.json() as Promise<{ session_id: number; org_id: number }>;
}

export async function submitAnswer(
  sessionId: number,
  questionId: string,
  answer: string,
) {
  const response = await fetch(
    `${API_BASE}/api/onboarding/session/${sessionId}/answer`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: questionId, answer }),
    },
  );
  if (!response.ok) {
    throw new Error("Failed to store answer");
  }
  return response.json();
}

export async function finalizeOnboarding(sessionId: number) {
  const response = await fetch(
    `${API_BASE}/api/onboarding/session/${sessionId}/finalize`,
    {
      method: "POST",
    },
  );
  if (!response.ok) {
    throw new Error("Failed to finalize onboarding");
  }
  return response.json() as Promise<{
    status: string;
    onboarding_stage: number;
    selected_packs: string[];
    confidence: number;
  }>;
}

export function streamSetupEvents(): EventSource {
  return new EventSource(`${API_BASE}/api/setup/events`);
}

export async function listPacks() {
  const response = await fetch(`${API_BASE}/api/packs`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load packs");
  }
  return response.json() as Promise<{ items: { id: string }[] }>;
}

export async function selectPacks(packIds: string[]) {
  const response = await fetch(`${API_BASE}/api/packs/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pack_ids: packIds }),
  });
  if (!response.ok) {
    throw new Error("Failed to select packs");
  }
  return response.json();
}
