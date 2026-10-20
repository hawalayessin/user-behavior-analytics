import PropTypes from "prop-types";
import {
  AlertTriangle,
  CheckCircle,
  Lightbulb,
  Search,
  Sparkles,
} from "lucide-react";

const SEVERITY_STYLES = {
  red: {
    backgroundColor: "var(--color-danger-bg)",
    borderColor: "rgba(239, 68, 68, 0.28)",
    color: "var(--color-danger)",
  },
  amber: {
    backgroundColor: "var(--color-amber-bg)",
    borderColor: "rgba(245, 158, 11, 0.28)",
    color: "var(--color-amber)",
  },
  green: {
    backgroundColor: "var(--color-success-bg)",
    borderColor: "rgba(34, 197, 94, 0.28)",
    color: "var(--color-success)",
  },
};

const ICONS = {
  alert: AlertTriangle,
  check: CheckCircle,
  lightbulb: Lightbulb,
  sparkles: Sparkles,
};

function InsightCard({ icon, title, message, severity }) {
  const palette = SEVERITY_STYLES[severity] || SEVERITY_STYLES.amber;
  const Icon = ICONS[icon] || ICONS.alert;

  return (
    <div
      className="rounded-xl border p-4"
      style={{
        backgroundColor: palette.backgroundColor,
        borderColor: palette.borderColor,
      }}
    >
      <p
        className="font-semibold text-sm mb-1 flex items-center gap-2"
        style={{ color: palette.color }}
      >
        <Icon size={15} />
        <span>{title}</span>
      </p>
      <p
        className="text-xs leading-relaxed opacity-90"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {message}
      </p>
    </div>
  );
}

export default function BIInsightsPanel({ insights, variant = "default" }) {
  const isOverview = variant === "overview";

  return (
    <div
      className="rounded-xl p-5"
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
      }}
    >
      <div className="mb-4">
        <h3
          className="text-sm font-semibold"
          style={{
            color: isOverview
              ? "var(--color-primary)"
              : "var(--color-text-primary)",
          }}
        >
          <span className="inline-flex items-center gap-2">
            <Search size={16} />
            Automated BI Insights
          </span>
        </h3>
        <p
          className="text-xs mt-0.5"
          style={{ color: "var(--color-text-muted)" }}
        >
          Real-time findings based on current platform data
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {insights.map((insight) => (
          <InsightCard key={insight.id} {...insight} />
        ))}
      </div>
    </div>
  );
}

BIInsightsPanel.propTypes = {
  variant: PropTypes.oneOf(["default", "overview"]),
  insights: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      severity: PropTypes.oneOf(["red", "amber", "green"]).isRequired,
      icon: PropTypes.oneOf(["alert", "check", "lightbulb", "sparkles"]),
      title: PropTypes.string.isRequired,
      message: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

InsightCard.propTypes = {
  icon: PropTypes.oneOf(["alert", "check", "lightbulb", "sparkles"]),
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  severity: PropTypes.oneOf(["red", "amber", "green"]).isRequired,
};
