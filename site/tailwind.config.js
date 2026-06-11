/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#0c0c12",
          raised: "#12121a",
          glass: "rgba(18, 18, 26, 0.72)",
        },
        accent: {
          DEFAULT: "#22d3ee",
          dim: "#0891b2",
          glow: "rgba(34, 211, 238, 0.15)",
        },
        ink: {
          DEFAULT: "#f0f4f8",
          muted: "#94a3b8",
          faint: "#64748b",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      backgroundImage: {
        mesh: `
          radial-gradient(ellipse 80% 60% at 10% 20%, rgba(34, 211, 238, 0.12), transparent 50%),
          radial-gradient(ellipse 60% 50% at 90% 80%, rgba(99, 102, 241, 0.1), transparent 50%),
          radial-gradient(ellipse 50% 40% at 50% 50%, rgba(34, 211, 238, 0.05), transparent 60%)
        `,
      },
      animation: {
        "fade-up": "fadeUp 0.6s ease-out forwards",
        "pulse-glow": "pulseGlow 3s ease-in-out infinite",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "0.8" },
        },
      },
    },
  },
  plugins: [],
};
