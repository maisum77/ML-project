/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#111111",
        newsprint: "#F9F9F7",
        "newsprint-muted": "#E5E5E0",
        "editorial-red": "#CC0000",
        "neutral-100": "#F5F5F5",
        "neutral-200": "#E5E5E5",
        "neutral-400": "#A3A3A3",
        "neutral-500": "#737373",
        "neutral-600": "#525252",
        "neutral-700": "#404040",
      },
      fontFamily: {
        serif: ["'Playfair Display'", "'Times New Roman'", "serif"],
        body: ["'Lora'", "Georgia", "serif"],
        sans: ["'Inter'", "'Helvetica Neue'", "sans-serif"],
        mono: ["'JetBrains Mono'", "'Courier New'", "monospace"],
      },
      borderRadius: {
        NONE: "0px",
      },
      maxWidth: {
        PAGE: "1280px",
      },
      boxShadow: {
        hard: "4px 4px 0px 0px #111111",
      },
      animation: {
        "ticker": "ticker 30s linear infinite",
      },
      keyframes: {
        ticker: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
    },
  },
  plugins: [],
};