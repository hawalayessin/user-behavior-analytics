import PropTypes from "prop-types"
import { ResponsiveContainer, FunnelChart, Funnel, LabelList, Tooltip } from "recharts"

export default function CampaignFunnelChart({ campaign }) {
  const target = Number(campaign?.target_size ?? 0)
  const activeSubs = Number(campaign?.active_subs ?? 0)
  const convPct = Number(campaign?.conv_rate ?? 0)
  const d7Pct = Number(campaign?.avg_d7 ?? 0)

  const d7Active = Math.round(activeSubs * (d7Pct / 100))

  const data = [
    { name: "Ciblés", value: target, fill: "#6366F1" },
    { name: "Subs actifs", value: activeSubs, fill: "#10B981" },
    { name: "Actifs D7", value: d7Active, fill: "#F59E0B" },
  ]

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-bold text-slate-100">Top Campaigns Funnel</h3>
          <p className="text-sm text-slate-400">
            {campaign?.name ? campaign.name : "Select a campaign from the table"}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-500">Conv%</p>
          <p className="text-sm font-semibold text-slate-100">{convPct.toFixed(2)}%</p>
          <p className="text-xs text-slate-500 mt-1">D7%</p>
          <p className="text-sm font-semibold text-slate-100">{d7Pct.toFixed(2)}%</p>
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <FunnelChart>
            <Tooltip
              contentStyle={{
                background: "#0F172A",
                border: "1px solid rgba(148,163,184,0.25)",
                borderRadius: 12,
              }}
              labelStyle={{ color: "#E2E8F0" }}
            />
            <Funnel dataKey="value" data={data} isAnimationActive>
              <LabelList position="right" fill="#E2E8F0" stroke="none" dataKey="name" />
              <LabelList position="center" fill="#0B1220" stroke="none" dataKey="value" />
            </Funnel>
          </FunnelChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-slate-900/40 border border-slate-700/40 rounded-lg p-3">
          <p className="text-xs text-slate-500">Ciblés</p>
          <p className="text-sm font-semibold text-slate-100">{target.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900/40 border border-slate-700/40 rounded-lg p-3">
          <p className="text-xs text-slate-500">Subs actifs</p>
          <p className="text-sm font-semibold text-slate-100">{activeSubs.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900/40 border border-slate-700/40 rounded-lg p-3">
          <p className="text-xs text-slate-500">Actifs D7 (est.)</p>
          <p className="text-sm font-semibold text-slate-100">{d7Active.toLocaleString()}</p>
        </div>
      </div>
    </div>
  )
}

CampaignFunnelChart.propTypes = {
  campaign: PropTypes.shape({
    name: PropTypes.string,
    target_size: PropTypes.number,
    total_subs: PropTypes.number,
    active_subs: PropTypes.number,
    conv_rate: PropTypes.number,
    avg_d7: PropTypes.number,
  }),
}

