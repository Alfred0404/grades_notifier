import plugin from "tailwindcss/plugin";

type Palette = {
  base: string;
  mantle: string;
  crust: string;
  text: string;
  subtext0: string;
  subtext1: string;
  surface0: string;
  surface1: string;
  surface2: string;
  overlay0: string;
  overlay1: string;
  overlay2: string;
  blue: string;
  green: string;
  red: string;
  yellow: string;
};

const palettes: Record<string, Palette> = {
  latte: {
    base: "239 241 245",
    mantle: "230 233 239",
    crust: "220 224 232",
    text: "76 79 105",
    subtext0: "108 111 133",
    subtext1: "92 95 119",
    surface0: "204 208 218",
    surface1: "188 192 204",
    surface2: "172 176 190",
    overlay0: "156 160 176",
    overlay1: "140 143 161",
    overlay2: "124 127 147",
    blue: "30 102 245",
    green: "64 160 43",
    red: "210 15 57",
    yellow: "223 142 29"
  },
  frappe: {
    base: "48 52 70",
    mantle: "41 44 60",
    crust: "35 38 52",
    text: "198 208 245",
    subtext0: "165 173 206",
    subtext1: "181 191 226",
    surface0: "65 69 89",
    surface1: "81 87 109",
    surface2: "98 104 128",
    overlay0: "115 121 148",
    overlay1: "131 139 167",
    overlay2: "148 156 187",
    blue: "140 170 238",
    green: "166 209 137",
    red: "231 130 132",
    yellow: "229 200 144"
  },
  macchiato: {
    base: "36 39 58",
    mantle: "30 32 48",
    crust: "24 25 38",
    text: "202 211 245",
    subtext0: "165 173 203",
    subtext1: "184 192 224",
    surface0: "54 58 79",
    surface1: "73 77 100",
    surface2: "91 96 120",
    overlay0: "110 115 141",
    overlay1: "128 135 162",
    overlay2: "147 154 183",
    blue: "138 173 244",
    green: "166 218 149",
    red: "237 135 150",
    yellow: "238 212 159"
  },
  mocha: {
    base: "30 30 46",
    mantle: "24 24 37",
    crust: "17 17 27",
    text: "205 214 244",
    subtext0: "166 173 200",
    subtext1: "186 194 222",
    surface0: "49 50 68",
    surface1: "69 71 90",
    surface2: "88 91 112",
    overlay0: "108 112 134",
    overlay1: "127 132 156",
    overlay2: "147 153 178",
    blue: "137 180 250",
    green: "166 227 161",
    red: "243 139 168",
    yellow: "249 226 175"
  }
};

export default plugin(({ addBase }) => {
  const themeVars: Record<string, Record<string, string>> = {};

  Object.entries(palettes).forEach(([themeName, palette]) => {
    themeVars[`[data-theme='${themeName}']`] = {
      "--ctp-base": palette.base,
      "--ctp-mantle": palette.mantle,
      "--ctp-crust": palette.crust,
      "--ctp-text": palette.text,
      "--ctp-subtext0": palette.subtext0,
      "--ctp-subtext1": palette.subtext1,
      "--ctp-surface0": palette.surface0,
      "--ctp-surface1": palette.surface1,
      "--ctp-surface2": palette.surface2,
      "--ctp-overlay0": palette.overlay0,
      "--ctp-overlay1": palette.overlay1,
      "--ctp-overlay2": palette.overlay2,
      "--ctp-blue": palette.blue,
      "--ctp-green": palette.green,
      "--ctp-red": palette.red,
      "--ctp-yellow": palette.yellow,
    };
  });

  addBase(themeVars);
});
