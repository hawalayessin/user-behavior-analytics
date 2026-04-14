export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        theme: {
          bg: "var(--color-bg-primary)",
          card: "var(--color-bg-card)",
          elevated: "var(--color-bg-elevated)",
          border: "var(--color-border)",
        },
        brand: {
          primary: "var(--color-primary)",
          success: "var(--color-success)",
          warning: "var(--color-warning)",
          danger: "var(--color-danger)",
          info: "var(--color-info)",
        },
        text: {
          primary: "var(--color-text-primary)",
          secondary: "var(--color-text-secondary)",
          muted: "var(--color-text-muted)",
        },
      },
    },
  },
  plugins: [],
}
