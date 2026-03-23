import React from "react"
import PropTypes from "prop-types"

function Chip({ children }) {
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs bg-slate-800 border border-slate-700 text-slate-200">
      {children}
    </span>
  )
}

export default function RiskSegmentsPanel({ data = [], onSelectSegment }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-100">Risk Segments</h3>
        <p className="text-sm text-slate-400 mt-1">Rule-based patterns that correlate with churn risk</p>
      </div>

      <div className="space-y-3">
        {(data ?? []).map((s) => (
          <button
            key={s.segment_id}
            onClick={() => onSelectSegment?.(s)}
            className="w-full text-left p-4 rounded-xl border border-slate-800 bg-slate-900 hover:bg-slate-800/40 transition"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-slate-100">{s.label}</h4>
                  <span className="text-[11px] px-2 py-0.5 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-300">
                    {Number(s.affected_users ?? 0).toLocaleString()} users
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">{s.description}</p>
              </div>
            </div>

            {!!(s.top_services?.length) && (
              <div className="flex flex-wrap gap-2 mt-3">
                {s.top_services.slice(0, 3).map((name) => (
                  <Chip key={name}>{name}</Chip>
                ))}
              </div>
            )}
          </button>
        ))}

        {(!data || data.length === 0) && (
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 text-sm text-slate-500">
            No risk segments available for the selected filters.
          </div>
        )}
      </div>
    </div>
  )
}

RiskSegmentsPanel.propTypes = {
  data: PropTypes.array,
  onSelectSegment: PropTypes.func,
}

