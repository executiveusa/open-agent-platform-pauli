"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const API_BASE = process.env.NEXT_PUBLIC_RUNS_API ?? "http://localhost:8000";

interface SnapshotItem {
  snapshot_id: string;
  reason: string;
  pack_versions: string;
}

export function OrgAdminPanel() {
  const [mode, setMode] = useState("tiered");
  const [expiresAt, setExpiresAt] = useState<string | null>(null);
  const [reason, setReason] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [snapshots, setSnapshots] = useState<SnapshotItem[]>([]);
  const [killSwitches, setKillSwitches] = useState({
    disable_agent_runs: false,
    disable_automerge: false,
  });

  useEffect(() => {
    fetch(`${API_BASE}/api/org/settings`, { cache: "no-store" })
      .then((response) => response.json())
      .then((data) => {
        setMode(data.autonomy_mode ?? "tiered");
        setExpiresAt(data.fuck_it_expires_at ?? null);
        setKillSwitches({
          disable_agent_runs: Boolean(data.disable_agent_runs),
          disable_automerge: Boolean(data.disable_automerge),
        });
      })
      .catch(() => undefined);
    fetch(`${API_BASE}/api/org/config/snapshots`, { cache: "no-store" })
      .then((response) => response.json())
      .then((data) => setSnapshots(data.items ?? []))
      .catch(() => setSnapshots([]));
  }, []);

  const updateMode = async (nextMode: string) => {
    await fetch(`${API_BASE}/api/org/settings/autonomy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode: nextMode,
        reason: reason || "manual",
        confirmation: confirmation || undefined,
      }),
    });
    setMode(nextMode);
  };

  const rollback = async (snapshotId: string) => {
    await fetch(`${API_BASE}/api/org/config/rollback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ snapshot_id: snapshotId }),
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Autonomy Mode</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground text-sm">
            Current mode: <span className="font-semibold">{mode}</span>
          </p>
          {expiresAt && (
            <p className="text-muted-foreground text-xs">
              Expires: {expiresAt}
            </p>
          )}
          <Input
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            placeholder="Reason for mode change"
          />
          <Input
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            placeholder='Type "FUCK IT MODE" to confirm'
          />
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => updateMode("tiered")}>Tiered mode</Button>
            <Button
              variant="destructive"
              onClick={() => updateMode("fuck_it")}
              disabled={confirmation !== "FUCK IT MODE"}
            >
              FUCK IT MODE
            </Button>
          </div>
          <div className="text-muted-foreground rounded-lg border p-3 text-xs">
            Kill switches: agent runs{" "}
            {killSwitches.disable_agent_runs ? "disabled" : "enabled"},
            automerge {killSwitches.disable_automerge ? "disabled" : "enabled"}.
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Config Snapshots</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {snapshots.length === 0 ? (
            <p className="text-muted-foreground text-sm">No snapshots yet.</p>
          ) : (
            snapshots.map((snap) => (
              <div
                key={snap.snapshot_id}
                className="flex flex-col gap-2 rounded-lg border p-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="font-medium">{snap.snapshot_id}</p>
                  <p className="text-muted-foreground text-xs">{snap.reason}</p>
                </div>
                <Button
                  size="sm"
                  onClick={() => rollback(snap.snapshot_id)}
                >
                  Roll back
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
