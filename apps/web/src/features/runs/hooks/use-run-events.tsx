import { useEffect, useMemo, useState } from "react";

export interface RunEvent {
  type: string;
  payload: string;
}

export function useRunEvents(runId: string | undefined) {
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [status, setStatus] = useState<string>("CONNECTING");

  const url = useMemo(() => {
    if (!runId) {
      return null;
    }
    const base = process.env.NEXT_PUBLIC_RUNS_API ?? "http://localhost:8000";
    return `${base}/api/runs/${runId}/events`;
  }, [runId]);

  useEffect(() => {
    if (!url) {
      return;
    }
    const source = new EventSource(url);
    source.addEventListener("status", (event) => {
      setStatus(event.data);
      setEvents((prev) => [...prev, { type: "status", payload: event.data }]);
    });
    source.addEventListener("session", (event) => {
      setEvents((prev) => [...prev, { type: "session", payload: event.data }]);
    });
    source.addEventListener("heal", (event) => {
      setEvents((prev) => [...prev, { type: "heal", payload: event.data }]);
    });
    source.addEventListener("message", (event) => {
      setEvents((prev) => [...prev, { type: "message", payload: event.data }]);
    });
    source.onerror = () => {
      setStatus("DISCONNECTED");
    };
    return () => {
      source.close();
    };
  }, [url]);

  return { events, status };
}
