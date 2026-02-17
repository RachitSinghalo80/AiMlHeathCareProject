/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FFFDF5", // Warm Cream
        foreground: "#1E293B", // Slate 800
        muted: "#F1F5F9",      // Slate 100
        "muted-foreground": "#64748B", // Slate 500
        accent: "#8B5CF6",     // Vivid Violet
        "accent-foreground": "#FFFFFF",
        secondary: "#F472B6",  // Hot Pink
        tertiary: "#FBBF24",   // Amber/Yellow
        quaternary: "#34D399", // Emerald/Mint
        border: "#E2E8F0",     // Slate 200
        input: "#FFFFFF",      // White
        card: "#FFFFFF",       // White
        ring: "#8B5CF6",       // Violet Focus
      },
      fontFamily: {
        heading: ['Outfit', 'system-ui', 'sans-serif'],
        body: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        sm: "8px",
        md: "16px",
        lg: "24px",
        xl: "32px",
        "2xl": "40px",
        // specialized for "blob" shapes if needed, usually handled via utilities
      },
      boxShadow: {
        "pop": "4px 4px 0px 0px #1E293B",
        "pop-hover": "6px 6px 0px 0px #1E293B",
        "pop-active": "2px 2px 0px 0px #1E293B",
        "sticker": "8px 8px 0px 0px #E2E8F0",
      },
      keyframes: {
        wiggle: {
          "0%, 100%": { transform: "rotate(0deg)" },
          "25%": { transform: "rotate(3deg)" },
          "75%": { transform: "rotate(-3deg)" },
        },
        popIn: {
          "0%": { transform: "scale(0)", opacity: "0" },
          "50%": { transform: "scale(1.1)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        }
      },
      animation: {
        wiggle: "wiggle 0.3s ease-in-out",
        popIn: "popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)",
      }
    },
  },
  plugins: [],
}
