import PropTypes from "prop-types";

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

function InsightCard({ icon, title, message, severity }) {
  const palette = SEVERITY_STYLES[severity] || SEVERITY_STYLES.amber;
  return (
    <div
      className="rounded-xl border p-4"
      style={{
        backgroundColor: palette.backgroundColor,
        borderColor: palette.borderColor,
      }}
    >
      <p className="font-semibold text-sm mb-1">
        {icon} {title}
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
          🔍 Automated BI Insights
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
      icon: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      message: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

InsightCard.propTypes = {
  icon: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
  severity: PropTypes.oneOf(["red", "amber", "green"]).isRequired,
};
