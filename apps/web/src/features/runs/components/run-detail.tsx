"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RunStatusChip } from "./run-status-chip";
import { useRunEvents } from "../hooks/use-run-events";
import type { RunDetail as RunDetailType } from "@/types/run";
import { getRun, getRunSession } from "../lib/api";
import { useI18n } from "@/i18n/provider";

export function RunDetail({ runId }: { runId: string }) {
  const [run, setRun] = useState<RunDetailType | null>(null);
  const [sessionUrl, setSessionUrl] = useState<string | null>(null);
  const { events, status } = useRunEvents(runId);
  const { dictionary } = useI18n();

  useEffect(() => {
    let mounted = true;
    getRun(runId)
      .then((data) => {
        if (mounted) {
          setRun(data);
        }
      })
      .catch(() => {
        setRun(null);
      });
    return () => {
      mounted = false;
    };
  }, [runId]);

  const handleSession = async () => {
    const session = await getRunSession(runId);
    setSessionUrl(session.url);
  };

  if (!run) {
    return (
      <Card>
        <CardContent className="py-6">{dictionary.runs.loading}</CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <div className="space-y-6">
        <Card>
          <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle>Run {run.run_id}</CardTitle>
              <p className="text-muted-foreground text-sm">
                Trace {run.trace_id ?? "pending"}
              </p>
            </div>
            <RunStatusChip status={run.status} />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-muted-foreground text-sm">
              {dictionary.runs.inputsLabel}: {run.inputs ?? "—"}
            </div>
            <div>
              <p className="text-sm font-medium">
                {dictionary.runs.eventsLabel}
              </p>
              <div className="text-muted-foreground mt-2 space-y-2 text-xs">
                {events.map((event, index) => (
                  <div key={`${event.type}-${index}`}>
                    <span className="font-semibold">{event.type}:</span>{" "}
                    {event.payload}
                  </div>
                ))}
              </div>
              <p className="text-muted-foreground mt-2 text-xs">
                {dictionary.runs.streamStatus}: {status}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{dictionary.runs.timelineTitle}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {run.steps.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                {dictionary.runs.noSteps}
              </p>
            ) : (
              run.steps.map((step) => (
                <div
                  key={step.order}
                  className="rounded-lg border p-3"
                >
                  <p className="text-sm font-semibold">
                    {dictionary.runs.stepLabel} {step.order}
                  </p>
                  <p className="text-muted-foreground text-xs">{step.status}</p>
                  <p className="text-xs">
                    {step.tool ?? dictionary.runs.toolPending}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
      <div className="space-y-6">
        <Card>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>{dictionary.runs.liveDesktop}</CardTitle>
            <Button
              size="sm"
              onClick={handleSession}
            >
              {dictionary.runs.startSession}
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {sessionUrl ? (
              <iframe
                src={sessionUrl}
                title="Live desktop"
                className="h-64 w-full rounded-md border"
              />
            ) : (
              <p className="text-muted-foreground text-sm">
                {dictionary.runs.liveDesktopEmpty}
              </p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{dictionary.runs.artifactsTitle}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {run.artifacts.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                {dictionary.runs.noArtifacts}
              </p>
            ) : (
              run.artifacts.map((artifact) => (
                <a
                  key={artifact.name}
                  href={artifact.url ?? "#"}
                  className="text-primary block text-sm"
                >
                  {artifact.name}
                </a>
              ))
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>{dictionary.runs.failuresTitle}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {run.failures.length === 0 ? (
              <p className="text-muted-foreground text-sm">
                {dictionary.runs.noFailures}
              </p>
            ) : (
              run.failures.map((failure, index) => (
                <div
                  key={`${failure.error}-${index}`}
                  className="rounded-lg border p-3"
                >
                  <p className="text-sm font-semibold">{failure.error}</p>
                  <p className="text-muted-foreground text-xs">
                    {failure.stack}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
