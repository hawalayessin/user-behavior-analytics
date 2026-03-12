import PropTypes from "prop-types"

export default function EngagementHealthPanel({ bars }) {
  // ── Guard ──────────────────────────────────────────────────
  if (!bars?.length) return null

  return (
    <div className="flex-1 bg-[#1A1D27] border border-slate-800 rounded-xl p-5">
      <h3 className="text-sm font-semibold text-white mb-4">
        Engagement Health Overview
      </h3>

      <div className="space-y-4">
        {bars.map((bar, i) => (
          <div key={i}>
            {/* Label + valeur */}
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400">{bar.label}</span>
              <span className="text-xs font-semibold text-slate-200">
                {bar.value}%
              </span>
            </div>

            {/* Progress bar */}
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width:      `${Math.min(bar.value, 100)}%`,
                  background: bar.color ?? "#7C3AED",
                }}
              />
            </div>

            {/* Sublabel + target */}
            <div className="flex items-center justify-between mt-1">
              <span className="text-xs text-slate-500">{bar.sublabel}</span>
              {bar.target !== null && bar.target !== undefined && (
                <span className="text-xs text-slate-600">
                  cible {bar.target}%
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

EngagementHealthPanel.propTypes = {
  bars: PropTypes.arrayOf(
    PropTypes.shape({
      label:    PropTypes.string,
      value:    PropTypes.number,
      target:   PropTypes.number,
      sublabel: PropTypes.string,
      color:    PropTypes.string,
    })
  ),
}