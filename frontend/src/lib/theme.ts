import type { ThemeName } from "../types";

const STORAGE_KEY = "grades_ui_theme";

export function getStoredTheme(): ThemeName {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "dark" ? "dark" : "light";
}

export function applyTheme(theme: ThemeName): void {
  localStorage.setItem(STORAGE_KEY, theme);
  document.documentElement.classList.toggle("p-dark", theme === "dark");
}

export function initTheme(): ThemeName {
  // If user has stored a preference, use it; otherwise follow system
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") {
    applyTheme(stored);
    return stored;
  }
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme: ThemeName = prefersDark ? "dark" : "light";
  applyTheme(theme);
  return theme;
}
