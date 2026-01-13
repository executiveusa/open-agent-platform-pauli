import { Badge } from "@/components/ui/badge";
import type { RunStatus } from "@/types/run";

const statusStyles: Record<RunStatus, string> = {
  QUEUED: "bg-slate-700 text-white",
  RUNNING: "bg-emerald-600 text-white",
  WAITING_TOOL: "bg-amber-500 text-white",
  NEEDS_APPROVAL: "bg-purple-600 text-white",
  FAILED: "bg-rose-600 text-white",
  COMPLETED: "bg-sky-600 text-white",
  CANCELED: "bg-gray-500 text-white",
};

export function RunStatusChip({ status }: { status: RunStatus }) {
  return (
    <Badge
      className={statusStyles[status]}
      variant="secondary"
    >
      {status}
    </Badge>
  );
}
