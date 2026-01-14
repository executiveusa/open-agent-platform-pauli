import { RunDetail } from "@/features/runs/components/run-detail";

interface RunDetailPageProps {
  params: { runId: string };
}

export default function RunDetailPage({ params }: RunDetailPageProps) {
  return (
    <div className="space-y-6 p-6">
      <RunDetail runId={params.runId} />
    </div>
  );
}
