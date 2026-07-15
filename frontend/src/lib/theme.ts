export const THEME_STORAGE_KEY = "cam-align-theme";

export type AppTheme = "google" | "google-dark" | "govuk" | "orange-dark";

export interface ThemeMeta {
  id: AppTheme;
  label: string;
  description: string;
  preview: { bg: string; accent: string };
  dark: boolean;
}

export const THEME_META: Record<AppTheme, ThemeMeta> = {
  govuk: {
    id: "govuk",
    label: "GOV.UK",
    description: "GDS Transport, crown black bar, green start button",
    preview: { bg: "#ffffff", accent: "#00703c" },
    dark: false,
  },
  google: {
    id: "google",
    label: "Light",
    description: "Material surfaces, Google blue, four-color accent bar",
    preview: { bg: "#ffffff", accent: "#1a73e8" },
    dark: false,
  },
  "google-dark": {
    id: "google-dark",
    label: "Dark",
    description: "Material dark surfaces, soft blue, four-color accent bar",
    preview: { bg: "#202124", accent: "#8ab4f8" },
    dark: true,
  },
  "orange-dark": {
    id: "orange-dark",
    label: "Orange Dark",
    description: "Matte black chrome, traffic orange, bold sans UI",
    preview: { bg: "#000000", accent: "#ff9900" },
    dark: true,
  },
};

export const THEME_LIST = Object.values(THEME_META);

/** @deprecated use THEME_LIST */
export const THEMES = THEME_LIST;

export const DEFAULT_THEME: AppTheme = "govuk";

export function readStoredTheme(): AppTheme {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored && stored in THEME_META) return stored as AppTheme;
  } catch {
    // localStorage may be blocked in embedded iframe
  }
  return DEFAULT_THEME;
}

export function themeIsDark(theme: AppTheme): boolean {
  return THEME_META[theme]?.dark ?? false;
}

export function applyTheme(theme: AppTheme) {
  const root = document.documentElement;
  root.dataset.theme = theme;
  const meta = THEME_META[theme];
  root.classList.toggle("dark", meta.dark);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // ignore
  }
}
