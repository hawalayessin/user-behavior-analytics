import PropTypes from "prop-types";

export default function EngagementHealthPanel({ bars }) {
  // ── Guard ──────────────────────────────────────────────────
  if (!bars?.length) return null;

  return (
    <div
      className="flex-1 rounded-xl p-5"
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <h3
        className="text-sm font-semibold mb-4"
        style={{ color: "var(--color-text-primary)" }}
      >
        Engagement Health Overview
      </h3>

      <div className="space-y-4">
        {bars.map((bar, i) => (
          <div key={i}>
            {/* Label + valeur */}
            <div className="flex items-center justify-between mb-1">
              <span
                className="text-xs"
                style={{ color: "var(--color-text-muted)" }}
              >
                {bar.label}
              </span>
              <span
                className="text-xs font-semibold"
                style={{ color: "var(--color-text-secondary)" }}
              >
                {bar.value}%
              </span>
            </div>

            {/* Progress bar */}
            <div
              className="h-2 rounded-full overflow-hidden"
              style={{ backgroundColor: "var(--color-bg-elevated)" }}
            >
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(bar.value, 100)}%`,
                  background: bar.color ?? "#7C3AED",
                }}
              />
            </div>

            {/* Sublabel + target */}
            <div className="flex items-center justify-between mt-1">
              <span
                className="text-xs"
                style={{ color: "var(--color-text-muted)" }}
              >
                {bar.sublabel}
              </span>
              {bar.target !== null && bar.target !== undefined && (
                <span
                  className="text-xs"
                  style={{ color: "var(--color-text-disabled)" }}
                >
                  cible {bar.target}%
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

EngagementHealthPanel.propTypes = {
  bars: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.number,
      target: PropTypes.number,
      sublabel: PropTypes.string,
      color: PropTypes.string,
    }),
  ),
};
