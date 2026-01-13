"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { RunStatusChip } from "./run-status-chip";
import type { RunSummary } from "@/types/run";
import { listRuns } from "../lib/api";
import Link from "next/link";
import { useI18n } from "@/i18n/provider";

export function RunList() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [filter, setFilter] = useState<string>("");
  const { dictionary } = useI18n();

  useEffect(() => {
    let mounted = true;
    listRuns()
      .then((items) => {
        if (mounted) {
          setRuns(items);
        }
      })
      .catch(() => {
        setRuns([]);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const filteredRuns = runs.filter((run) =>
    run.status.toLowerCase().includes(filter.toLowerCase()),
  );

  return (
    <Card>
      <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <CardTitle>{dictionary.runs.title}</CardTitle>
          <p className="text-muted-foreground text-sm">
            {dictionary.runs.subtitle}
          </p>
        </div>
        <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row sm:items-center">
          <Input
            placeholder={dictionary.runs.filterPlaceholder}
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          />
          <Button>{dictionary.runs.runCta}</Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {filteredRuns.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            {dictionary.runs.empty}
          </p>
        ) : (
          filteredRuns.map((run) => (
            <Link
              key={run.run_id}
              href={`/runs/${run.run_id}`}
              className="hover:border-primary block rounded-lg border p-4 transition"
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-medium">
                    {dictionary.runs.runLabel} {run.run_id.slice(0, 8)}
                  </p>
                  <p className="text-muted-foreground text-xs">
                    {new Date(run.created_at).toLocaleString()}
                  </p>
                </div>
                <RunStatusChip status={run.status} />
              </div>
            </Link>
          ))
        )}
      </CardContent>
    </Card>
  );
}
