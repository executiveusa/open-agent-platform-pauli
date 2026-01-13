"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getDictionary, locales, type Dictionary, type Locale } from "./index";

interface I18nContextValue {
  locale: Locale;
  dictionary: Dictionary;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

const defaultLocale: Locale = "en";

function pickLocale(preferred: readonly string[]): Locale {
  const fallback = locales.find((locale) => preferred.includes(locale));
  return fallback ?? defaultLocale;
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>(defaultLocale);

  useEffect(() => {
    const stored = window.localStorage.getItem("locale");
    if (stored && locales.includes(stored as Locale)) {
      setLocale(stored as Locale);
      return;
    }
    const preferred = navigator.languages?.length
      ? navigator.languages
      : [navigator.language];
    setLocale(pickLocale(preferred));
  }, []);

  const dictionary = useMemo(() => getDictionary(locale), [locale]);

  return (
    <I18nContext.Provider value={{ locale, dictionary }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    return { locale: defaultLocale, dictionary: getDictionary(defaultLocale) };
  }
  return context;
}
