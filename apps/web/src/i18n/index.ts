import { en } from "./translations/en";
import { es } from "./translations/es";
import { esMX } from "./translations/es-MX";
import { itIT } from "./translations/it-IT";

export const locales = ["it-IT", "es-MX", "es", "en"] as const;
export type Locale = (typeof locales)[number];

const dictionary = {
  "it-IT": itIT,
  "es-MX": esMX,
  es,
  en,
};

export type Dictionary = typeof en;

export function getDictionary(locale: Locale): Dictionary {
  return dictionary[locale] ?? en;
}
