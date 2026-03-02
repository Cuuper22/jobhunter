/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          primary: "oklch(0.13 0.015 260)",
          secondary: "oklch(0.17 0.015 260)",
          elevated: "oklch(0.22 0.015 260)",
        },
        accent: {
          primary: "oklch(0.65 0.18 260)",
          "primary-dim": "oklch(0.45 0.12 260)",
          secondary: "oklch(0.70 0.10 170)",
          "secondary-dim": "oklch(0.50 0.07 170)",
        },
        ink: {
          heading: "oklch(0.95 0.003 250)",
          body: "oklch(0.92 0.005 250)",
          muted: "oklch(0.65 0.01 250)",
          faint: "oklch(0.40 0.005 250)",
        },
        edge: {
          DEFAULT: "oklch(0.28 0.015 260)",
          strong: "oklch(0.38 0.015 260)",
        },
        signal: {
          success: "oklch(0.70 0.17 155)",
          warning: "oklch(0.78 0.15 80)",
          error: "oklch(0.65 0.20 25)",
          info: "oklch(0.65 0.18 260)",
        },
      },
      borderRadius: {
        sm: "6px",
        md: "8px",
        lg: "12px",
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "'Inter'", "system-ui", "sans-serif"],
        body: ["'Inter'", "'Helvetica Neue'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "'SF Mono'", "'Cascadia Code'", "monospace"],
      },
      letterSpacing: {
        heading: "-0.02em",
      },
      boxShadow: {
        sm: "0 1px 2px oklch(0.3 0.02 260 / 0.06)",
        md: "0 2px 8px oklch(0.3 0.02 260 / 0.08)",
      },
    },
  },
  plugins: [],
};
