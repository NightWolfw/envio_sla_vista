/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./lib/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#0f172a",
        surface: "#1e293b",
        surfaceMuted: "#334155",
        border: "#475569",
        text: "#e2e8f0",
        textMuted: "#cbd5f5",
        accent: "#22d3ee",
        accentMuted: "#0f172a"
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "system-ui", "-apple-system", "sans-serif"]
      },
      boxShadow: {
        panel: "0 25px 45px -30px rgba(15, 23, 42, 0.8)"
      },
      borderRadius: {
        xl: "0.85rem",
        "2xl": "1.2rem"
      }
    }
  },
  plugins: []
};
