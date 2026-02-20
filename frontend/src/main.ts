import { createApp } from "vue";
import PrimeVue from "primevue/config";
import Tooltip from "primevue/tooltip";
import Aura from "@primevue/themes/aura";
import { definePreset } from "@primevue/themes";
import "primeicons/primeicons.css";
import "@fontsource-variable/inter";
import "./style.css";
import App from "./App.vue";

// Override dark mode surface palette to be near-black / near-white
const NoirAura = definePreset(Aura, {
  semantic: {
    primary: {
      50: "#fafafa",
      100: "#f4f4f5",
      200: "#e4e4e7",
      300: "#d4d4d8",
      400: "#a1a1aa",
      500: "#71717a",
      600: "#52525b",
      700: "#3f3f46",
      800: "#27272a",
      900: "#18181b",
      950: "#09090b",
    },
    colorScheme: {
      dark: {
        primary: {
          color: "#fafafa",
          contrastColor: "#09090b",
          hoverColor: "#e4e4e7",
          activeColor: "#d4d4d8",
        },
        highlight: {
          background: "#fafafa",
          focusBackground: "#e4e4e7",
          color: "#09090b",
          focusColor: "#09090b",
        },
        surface: {
          0: "#ffffff",
          50: "#fafafa",
          100: "#f4f4f5",
          200: "#e4e4e7",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
          600: "#3f3f46",
          700: "#27272a",
          800: "#18181b",
          900: "#0e0e10",
          950: "#09090b",
        },
      },
    },
  },
});

const app = createApp(App);

app.use(PrimeVue, {
  theme: {
    preset: NoirAura,
    options: {
      darkModeSelector: ".p-dark",
      cssLayer: false,
    },
  },
});

app.directive("tooltip", Tooltip);
app.mount("#app");
