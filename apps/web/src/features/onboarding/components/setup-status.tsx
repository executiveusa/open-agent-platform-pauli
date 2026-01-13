"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18n } from "@/i18n/provider";
import { listPacks, selectPacks, streamSetupEvents } from "../lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function SetupStatus() {
  const { dictionary } = useI18n();
  const [status, setStatus] = useState("CONNECTING");
  const [events, setEvents] = useState<string[]>([]);
  const [selectedPacks, setSelectedPacks] = useState<string[]>([]);
  const [confidence, setConfidence] = useState<string>("0");
  const [availablePacks, setAvailablePacks] = useState<string[]>([]);
  const [overrideValue, setOverrideValue] = useState("");

  useEffect(() => {
    const packs = window.sessionStorage.getItem("onboarding_selected_packs");
    const storedConfidence = window.sessionStorage.getItem(
      "onboarding_confidence",
    );
    if (packs) {
      setSelectedPacks(JSON.parse(packs));
    }
    if (storedConfidence) {
      setConfidence(storedConfidence);
    }
    const source = streamSetupEvents();
    source.addEventListener("status", (event) => {
      setStatus(event.data);
      setEvents((prev) => [...prev, event.data]);
    });
    source.onerror = () => {
      setStatus("DISCONNECTED");
    };
    return () => {
      source.close();
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    listPacks()
      .then((response) => {
        if (mounted) {
          setAvailablePacks(response.items.map((item) => item.id));
        }
      })
      .catch(() => {
        setAvailablePacks([]);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const handleOverride = async () => {
    const packs = overrideValue
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
    if (packs.length === 0) {
      return;
    }
    await selectPacks(packs);
    setSelectedPacks(packs);
  };

  return (
    <Card className="border-none bg-gradient-to-br from-[#111827] via-[#1E3A8A] to-[#0F172A] text-white">
      <CardHeader>
        <CardTitle className="text-2xl">
          {dictionary.onboarding.setupTitle}
        </CardTitle>
        <p className="text-sm text-white/70">
          {dictionary.onboarding.setupBody}
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="rounded-xl bg-white/10 p-4">
          <p className="text-base font-semibold">{status}</p>
          <p className="text-white/70">{dictionary.onboarding.setupHint}</p>
        </div>
        <div className="rounded-xl bg-white/10 p-4 text-sm">
          <p className="font-semibold">{dictionary.onboarding.packTitle}</p>
          <p className="text-white/70">
            {dictionary.onboarding.packConfidence}: {confidence}
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {selectedPacks.length === 0 ? (
              <span className="text-white/70">
                {dictionary.onboarding.packEmpty}
              </span>
            ) : (
              selectedPacks.map((pack) => (
                <span
                  key={pack}
                  className="rounded-full bg-white/20 px-3 py-1"
                >
                  {pack}
                </span>
              ))
            )}
          </div>
          <div className="mt-3 space-y-2">
            <p className="text-xs text-white/70">
              {dictionary.onboarding.packOverrideHint}
            </p>
            <Input
              value={overrideValue}
              onChange={(event) => setOverrideValue(event.target.value)}
              placeholder={availablePacks.join(", ")}
            />
            <Button
              size="sm"
              onClick={handleOverride}
            >
              {dictionary.onboarding.packOverrideAction}
            </Button>
          </div>
        </div>
        <div className="space-y-2 text-sm text-white/70">
          {events.map((event, index) => (
            <p key={`${event}-${index}`}>{event}</p>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
