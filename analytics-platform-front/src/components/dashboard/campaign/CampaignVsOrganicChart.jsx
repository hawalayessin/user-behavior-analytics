import PropTypes from "prop-types"
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Brush,
} from "recharts"

export default function CampaignVsOrganicChart({ data }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
      <div>
        <h3 className="text-lg font-bold text-slate-100">Campaign vs Organic</h3>
        <p className="text-sm text-slate-400">Monthly subscriptions (campaign-linked vs organic)</p>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data ?? []} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.15)" />
            <XAxis dataKey="month" tick={{ fill: "#94A3B8", fontSize: 11 }} />
            <YAxis tick={{ fill: "#94A3B8", fontSize: 11 }} />
            <Tooltip
              contentStyle={{
                background: "#0F172A",
                border: "1px solid rgba(148,163,184,0.25)",
                borderRadius: 12,
              }}
              labelStyle={{ color: "#E2E8F0" }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="campaign_subs"
              name="Campaign subs"
              stroke="#6366F1"
              fill="rgba(99,102,241,0.25)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="organic_subs"
              name="Organic subs"
              stroke="#94A3B8"
              fill="rgba(148,163,184,0.18)"
              strokeWidth={2}
            />
            <Brush dataKey="month" height={22} stroke="#6366F1" travellerWidth={12} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

CampaignVsOrganicChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      month: PropTypes.string.isRequired,
      campaign_subs: PropTypes.number,
      organic_subs: PropTypes.number,
    })
  ),
}

