import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18n } from "@/i18n/provider";

export function JarvisHero() {
  const { dictionary } = useI18n();
  return (
    <Card className="overflow-hidden border-none bg-gradient-to-br from-[#2B1E5B] via-[#1E3A8A] to-[#0F172A] text-white">
      <CardHeader>
        <CardTitle className="text-2xl">{dictionary.jarvis.title}</CardTitle>
        <p className="text-sm text-white/70">{dictionary.jarvis.subtitle}</p>
      </CardHeader>
      <CardContent className="grid gap-4 text-sm">
        <div className="rounded-xl bg-white/10 p-4">
          <p className="text-base font-semibold">
            {dictionary.jarvis.nowRunningTitle}
          </p>
          <p className="text-white/70">{dictionary.jarvis.nowRunningBody}</p>
        </div>
        <div className="rounded-xl bg-white/10 p-4">
          <p className="text-base font-semibold">
            {dictionary.jarvis.healingTitle}
          </p>
          <p className="text-white/70">{dictionary.jarvis.healingBody}</p>
        </div>
        <div className="rounded-xl bg-white/10 p-4">
          <p className="text-base font-semibold">
            {dictionary.jarvis.liveDesktopTitle}
          </p>
          <p className="text-white/70">{dictionary.jarvis.liveDesktopBody}</p>
        </div>
      </CardContent>
    </Card>
  );
}
