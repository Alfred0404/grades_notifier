// Dark mode: interpolate #e56c6c (grade 0) → #46d57e (grade 20)
const DARK_RED = { r: 229, g: 108, b: 108 };
const DARK_GREEN = { r: 70, g: 213, b: 126 };

function lerpChannel(a: number, b: number, t: number) {
  return Math.round(a + (b - a) * t);
}

function darkGradeColor(grade: number): { background: string; color: string } {
  const t = Math.max(0, Math.min(20, grade)) / 20;
  const r = lerpChannel(DARK_RED.r, DARK_GREEN.r, t);
  const g = lerpChannel(DARK_RED.g, DARK_GREEN.g, t);
  const b = lerpChannel(DARK_RED.b, DARK_GREEN.b, t);
  return {
    background: `rgba(${r}, ${g}, ${b}, 0.18)`,
    color: `rgb(${r}, ${g}, ${b})`,
  };
}

export function getGradeColor(
  grade: number | null,
  isDark: boolean,
): { background: string; color: string } {
  if (grade === null || Number.isNaN(grade)) {
    return { background: "transparent", color: "inherit" };
  }
  if (isDark) {
    return darkGradeColor(grade);
  }
  // Light mode: HSL green-red scale
  const clamped = Math.max(0, Math.min(20, grade));
  const hue = (clamped / 20) * 120;
  return {
    background: `hsl(${hue.toFixed(1)} 68% 72% / 0.40)`,
    color: `hsl(${hue.toFixed(1)} 60% 20%)`,
  };
}
