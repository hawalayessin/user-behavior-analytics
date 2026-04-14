import PropTypes from "prop-types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-400 mb-1">{label?.replace("\n", " ")}</p>
      <p className="text-slate-100 font-semibold">
        {payload[0].value.toLocaleString()} drop-offs
      </p>
    </div>
  );
};

export default function TrialDropoffChart({ data }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex-[1]">
      <h3 className="text-sm font-semibold text-slate-100 mb-4">
        Free Trial Drop-off by Day
      </h3>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart
          data={data}
          margin={{ top: 4, right: 8, left: -10, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
          <XAxis
            dataKey="label"
            tick={{ fill: "#94A3B8", fontSize: 11 }}
            tickFormatter={(v) => v.split("\n")[0]}
          />
          <YAxis tick={{ fill: "#94A3B8", fontSize: 11 }} />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: "rgba(255,255,255,0.04)" }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* BI Annotation */}
      <div className="mt-3 bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs p-3 rounded-lg">
        ⚠ Day 3 (48–72h) is the critical conversion decision point. Users who
        fail to convert by 72h show ~94% churn probability. Focus retention
        efforts on the first 3 days.
      </div>
    </div>
  );
}

TrialDropoffChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
};
CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
  label: PropTypes.string,
};
