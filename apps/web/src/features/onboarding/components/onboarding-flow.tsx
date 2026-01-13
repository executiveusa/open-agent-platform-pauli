"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/i18n/provider";
import {
  fetchOnboardingTemplate,
  finalizeOnboarding,
  submitAnswer,
} from "../lib/api";
import { useRouter } from "next/navigation";

interface Question {
  id: string;
  type: string;
  required: boolean;
  choices?: string[];
  prompt: Record<string, string>;
}

export function OnboardingFlow() {
  const { dictionary, locale } = useI18n();
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [minFields, setMinFields] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isRecording, setIsRecording] = useState(false);

  useEffect(() => {
    const stored = window.sessionStorage.getItem("onboarding_session_id");
    if (stored) {
      setSessionId(Number(stored));
    }
  }, []);

  useEffect(() => {
    let mounted = true;
    fetchOnboardingTemplate()
      .then((template) => {
        if (!mounted) {
          return;
        }
        const flattened = template.stages.flatMap((stage) => stage.questions);
        setQuestions(flattened);
        setMinFields(template.min_stage_fields ?? []);
      })
      .catch(() => {
        setQuestions([]);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const currentQuestion = questions[currentIndex];
  const prompt = useMemo(() => {
    if (!currentQuestion) {
      return "";
    }
    return (
      currentQuestion.prompt[locale] ??
      currentQuestion.prompt.en ??
      dictionary.onboarding.loadingPrompt
    );
  }, [currentQuestion, locale, dictionary.onboarding.loadingPrompt]);

  const progressValue = questions.length
    ? Math.round(((currentIndex + 1) / questions.length) * 100)
    : 0;

  const canFinish = currentIndex >= questions.length - 1;
  const minFieldsDone = minFields.every((field) => Boolean(answers[field]));

  const handleSubmit = useCallback(async () => {
    if (!currentQuestion || !sessionId) {
      return;
    }
    await submitAnswer(sessionId, currentQuestion.id, answer || "");
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: answer }));
    setAnswer("");
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      return;
    }
    const result = await finalizeOnboarding(sessionId);
    window.sessionStorage.setItem(
      "onboarding_selected_packs",
      JSON.stringify(result.selected_packs ?? []),
    );
    window.sessionStorage.setItem(
      "onboarding_confidence",
      result.confidence?.toString() ?? "0",
    );
    router.push("/setup");
  }, [
    answer,
    currentIndex,
    currentQuestion,
    questions.length,
    router,
    sessionId,
  ]);

  const handleFinishLater = useCallback(async () => {
    if (!sessionId || !minFieldsDone) {
      return;
    }
    const result = await finalizeOnboarding(sessionId);
    window.sessionStorage.setItem(
      "onboarding_selected_packs",
      JSON.stringify(result.selected_packs ?? []),
    );
    window.sessionStorage.setItem(
      "onboarding_confidence",
      result.confidence?.toString() ?? "0",
    );
    router.push("/setup");
  }, [minFieldsDone, router, sessionId]);

  const handleVoice = () => {
    const SpeechRecognition =
      (
        window as typeof window & {
          webkitSpeechRecognition?: typeof SpeechRecognition;
          SpeechRecognition?: typeof SpeechRecognition;
        }
      ).SpeechRecognition ||
      (
        window as typeof window & {
          webkitSpeechRecognition?: typeof SpeechRecognition;
        }
      ).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = locale;
    recognition.onstart = () => setIsRecording(true);
    recognition.onend = () => setIsRecording(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript ?? "";
      setAnswer(transcript);
    };
    recognition.start();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{dictionary.onboarding.flowTitle}</CardTitle>
        <p className="text-muted-foreground text-sm">
          {dictionary.onboarding.flowBody}
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={progressValue} />
        <div className="rounded-lg border p-4">
          <p className="text-sm font-semibold">{prompt}</p>
          {currentQuestion?.choices ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {currentQuestion.choices.map((choice) => (
                <Button
                  key={choice}
                  variant={answer === choice ? "default" : "secondary"}
                  size="sm"
                  onClick={() => setAnswer(choice)}
                >
                  {choice}
                </Button>
              ))}
            </div>
          ) : (
            <Input
              className="mt-3"
              placeholder={dictionary.onboarding.answerPlaceholder}
              value={answer}
              onChange={(event) => setAnswer(event.target.value)}
            />
          )}
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Button
            onClick={handleVoice}
            variant="secondary"
          >
            {isRecording
              ? dictionary.onboarding.listening
              : dictionary.onboarding.pushToTalk}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!currentQuestion}
          >
            {canFinish
              ? dictionary.onboarding.finish
              : dictionary.onboarding.next}
          </Button>
          <Button
            variant="outline"
            onClick={handleFinishLater}
            disabled={!minFieldsDone}
          >
            {dictionary.onboarding.finishLater}
          </Button>
        </div>
        <p className="text-muted-foreground text-xs">
          {dictionary.onboarding.textFallback}
        </p>
      </CardContent>
    </Card>
  );
}
