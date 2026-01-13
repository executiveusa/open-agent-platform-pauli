"use client";

import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useI18n } from "@/i18n/provider";
import { startOnboardingSession } from "../lib/api";
import { useRouter } from "next/navigation";

const personas = [
  { id: "calm", label: "Calm" },
  { id: "energetic", label: "Energetic" },
  { id: "formal", label: "Formal" },
];

export function WelcomeCard() {
  const { dictionary, locale } = useI18n();
  const router = useRouter();
  const [persona, setPersona] = useState(personas[0]?.id ?? "calm");
  const [orgName, setOrgName] = useState("");
  const videoSrc = useMemo(() => `/videos/intro-${locale}.mp4`, [locale]);

  const handleStart = async () => {
    const session = await startOnboardingSession({
      locale,
      persona: { style: persona },
      orgName: orgName || undefined,
    });
    window.sessionStorage.setItem(
      "onboarding_session_id",
      session.session_id.toString(),
    );
    router.push("/onboarding");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{dictionary.onboarding.welcomeTitle}</CardTitle>
        <p className="text-muted-foreground text-sm">
          {dictionary.onboarding.welcomeBody}
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="overflow-hidden rounded-lg border">
          <video
            className="h-64 w-full object-cover"
            controls
          >
            <source
              src={videoSrc}
              type="video/mp4"
            />
            {dictionary.onboarding.videoFallback}
          </video>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">
              {dictionary.onboarding.personaLabel}
            </label>
            <Select
              value={persona}
              onValueChange={setPersona}
            >
              <SelectTrigger>
                <SelectValue
                  placeholder={dictionary.onboarding.personaPlaceholder}
                />
              </SelectTrigger>
              <SelectContent>
                {personas.map((item) => (
                  <SelectItem
                    key={item.id}
                    value={item.id}
                  >
                    {item.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">
              {dictionary.onboarding.orgLabel}
            </label>
            <Input
              placeholder={dictionary.onboarding.orgPlaceholder}
              value={orgName}
              onChange={(event) => setOrgName(event.target.value)}
            />
          </div>
        </div>
        <div className="text-muted-foreground rounded-lg border border-dashed p-4 text-sm">
          {dictionary.onboarding.demoNote}
        </div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Button onClick={handleStart}>
            {dictionary.onboarding.startVoice}
          </Button>
          <Button
            variant="secondary"
            onClick={handleStart}
          >
            {dictionary.onboarding.startText}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
