"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_RUNS_API ?? "http://localhost:8000";

export function TelemetrySummary() {
  const [items, setItems] = useState<string[]>([]);

  useEffect(() => {
    let mounted = true;
    fetch(`${API_BASE}/api/telemetry/org-summary`, { cache: "no-store" })
      .then((response) => response.json())
      .then((data) => {
        if (mounted) {
          setItems(
            (data.items ?? []).map(
              (item: { metrics_json: string }) => item.metrics_json,
            ),
          );
        }
      })
      .catch(() => {
        setItems([]);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Telemetry Insights</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {items.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            No telemetry data yet.
          </p>
        ) : (
          items.map((item, index) => (
            <pre
              key={`${item}-${index}`}
              className="text-muted-foreground text-xs"
            >
              {item}
            </pre>
          ))
        )}
      </CardContent>
    </Card>
  );
}
