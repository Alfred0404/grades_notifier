import type { Config } from "tailwindcss";
import catppuccinPlugin from "./tailwind.catppuccin.plugin";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "rgb(var(--ctp-base) / <alpha-value>)",
        mantle: "rgb(var(--ctp-mantle) / <alpha-value>)",
        crust: "rgb(var(--ctp-crust) / <alpha-value>)",
        text: "rgb(var(--ctp-text) / <alpha-value>)",
        subtext0: "rgb(var(--ctp-subtext0) / <alpha-value>)",
        subtext1: "rgb(var(--ctp-subtext1) / <alpha-value>)",
        surface0: "rgb(var(--ctp-surface0) / <alpha-value>)",
        surface1: "rgb(var(--ctp-surface1) / <alpha-value>)",
        surface2: "rgb(var(--ctp-surface2) / <alpha-value>)",
        overlay0: "rgb(var(--ctp-overlay0) / <alpha-value>)",
        overlay1: "rgb(var(--ctp-overlay1) / <alpha-value>)",
        overlay2: "rgb(var(--ctp-overlay2) / <alpha-value>)",
        ctpBlue: "rgb(var(--ctp-blue) / <alpha-value>)",
      },
    },
  },
  plugins: [catppuccinPlugin],
} satisfies Config;
