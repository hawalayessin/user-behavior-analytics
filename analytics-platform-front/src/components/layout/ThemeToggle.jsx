import { Sun, Moon } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";

export function ThemeToggle({ className = "" }) {
  const { toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`relative inline-flex items-center justify-center w-10 h-10 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
      style={{
        backgroundColor: "var(--color-bg-elevated)",
        border: "1px solid var(--color-border)",
        color: "var(--color-text-muted)",
      }}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      {isDark ? (
        <Sun
          size={18}
          style={{ color: "var(--color-amber)" }}
          className="transition-transform duration-200 hover:rotate-12"
        />
      ) : (
        <Moon
          size={18}
          style={{ color: "var(--color-primary)" }}
          className="transition-transform duration-200"
        />
      )}
    </button>
  );
}

export function ThemeToggleWithLabel() {
  const { toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-left transition-all duration-200"
      style={{
        backgroundColor: "transparent",
        color: "var(--color-text-muted)",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = "var(--color-bg-elevated)";
        e.currentTarget.style.color = "var(--color-text-primary)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = "transparent";
        e.currentTarget.style.color = "var(--color-text-muted)";
      }}
    >
      <span
        className="flex items-center justify-center w-8 h-8 rounded-lg"
        style={{ backgroundColor: "var(--color-bg-elevated)" }}
      >
        {isDark ? (
          <Sun size={16} style={{ color: "var(--color-amber)" }} />
        ) : (
          <Moon size={16} style={{ color: "var(--color-primary)" }} />
        )}
      </span>
      <span className="text-sm font-medium">
        {isDark ? "Light Mode" : "Dark Mode"}
      </span>

      <span
        className="ml-auto relative inline-flex h-5 w-9 rounded-full transition-colors duration-200"
        style={{
          backgroundColor: isDark
            ? "var(--color-border)"
            : "var(--color-primary)",
        }}
      >
        <span
          className="absolute top-0.5 left-0.5 inline-block h-4 w-4 rounded-full bg-white shadow transition-transform duration-200"
          style={{
            transform: isDark ? "translateX(0)" : "translateX(16px)",
          }}
        />
      </span>
    </button>
  );
}
