"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface PackItem {
  pack_id: string;
  version: string;
  type: string;
}

const API_BASE = process.env.NEXT_PUBLIC_RUNS_API ?? "http://localhost:8000";

export function MarketplaceList() {
  const [packs, setPacks] = useState<PackItem[]>([]);

  useEffect(() => {
    let mounted = true;
    fetch(`${API_BASE}/api/marketplace/packs`, { cache: "no-store" })
      .then((response) => response.json())
      .then((data) => {
        if (mounted) {
          setPacks(data.items ?? []);
        }
      })
      .catch(() => {
        setPacks([]);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const postAction = async (path: string, packId: string) => {
    await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pack_id: packId }),
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Marketplace Packs</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {packs.length === 0 ? (
          <p className="text-muted-foreground text-sm">No packs available.</p>
        ) : (
          packs.map((pack) => (
            <div
              key={pack.pack_id}
              className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <p className="font-medium">{pack.pack_id}</p>
                <p className="text-muted-foreground text-xs">
                  {pack.type} · {pack.version}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={() =>
                    postAction("/api/marketplace/install", pack.pack_id)
                  }
                >
                  Install
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() =>
                    postAction("/api/marketplace/enable", pack.pack_id)
                  }
                >
                  Enable
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() =>
                    postAction("/api/marketplace/disable", pack.pack_id)
                  }
                >
                  Disable
                </Button>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
