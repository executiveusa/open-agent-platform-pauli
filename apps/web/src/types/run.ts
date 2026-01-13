export type RunStatus =
  | "QUEUED"
  | "RUNNING"
  | "WAITING_TOOL"
  | "NEEDS_APPROVAL"
  | "FAILED"
  | "COMPLETED"
  | "CANCELED";

export interface RunSummary {
  id: number;
  run_id: string;
  status: RunStatus;
  trace_id?: string | null;
  model_used?: string | null;
  created_at: string;
}

export interface RunDetail extends RunSummary {
  inputs?: string | null;
  steps: {
    order: number;
    status: string;
    tool?: string | null;
    inputs?: string | null;
    outputs?: string | null;
    created_at: string;
  }[];
  artifacts: { name: string; url?: string | null }[];
  failures: {
    error: string;
    stack?: string | null;
    metadata?: string | null;
    screenshot_url?: string | null;
    created_at: string;
  }[];
}
