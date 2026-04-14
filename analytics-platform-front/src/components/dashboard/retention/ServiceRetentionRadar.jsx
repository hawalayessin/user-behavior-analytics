import PropTypes from "prop-types";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const RADAR_METRICS = ["D7", "D14", "D30", "Users", "Cohorts"];

export default function ServiceRetentionRadar({ data }) {
  if (!data?.length) {
    return (
      <div
        className="rounded-xl p-6 h-full flex items-center justify-center text-sm"
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          color: "var(--color-text-muted)",
          boxShadow: "var(--color-card-shadow)",
        }}
      >
        No service radar data
      </div>
    );
  }

  const maxUsers = Math.max(...data.map((d) => d.total_users || 0), 1);
  const maxCohorts = Math.max(...data.map((d) => d.cohort_count || 0), 1);

  const chartData = RADAR_METRICS.map((metric) => ({
    metric,
    ...Object.fromEntries(
      data.map((s) => {
        if (metric === "D7") return [s.service, s.d7];
        if (metric === "D14") return [s.service, s.d14];
        if (metric === "D30") return [s.service, s.d30];
        if (metric === "Users") {
          const norm = ((s.total_users || 0) / maxUsers) * 100;
          return [s.service, norm];
        }
        if (metric === "Cohorts") {
          const norm = ((s.cohort_count || 0) / maxCohorts) * 100;
          return [s.service, norm];
        }
        return [s.service, 0];
      }),
    ),
  }));

  const colors = [
    "#6366F1",
    "#10B981",
    "#F59E0B",
    "#EC4899",
    "#22C55E",
    "#3B82F6",
  ];

  return (
    <div
      className="rounded-xl p-6 h-full flex flex-col"
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
        Service Retention Radar
      </h3>
      <div className="flex-1 min-h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
            <PolarGrid stroke="var(--chart-grid)" />
            <PolarAngleAxis
              dataKey="metric"
              tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={30}
              tick={{ fill: "var(--color-text-disabled)", fontSize: 10 }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--chart-tooltip-bg)",
                border: "1px solid var(--chart-tooltip-border)",
                borderRadius: "0.5rem",
                fontSize: "0.75rem",
                color: "var(--color-text-primary)",
              }}
              formatter={(value, name) => [`${value.toFixed(1)}%`, name]}
            />
            <Legend
              formatter={(value) => (
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--color-text-muted)",
                  }}
                >
                  {value}
                </span>
              )}
            />
            {data.map((s, idx) => (
              <Radar
                key={s.service}
                name={s.service}
                dataKey={s.service}
                stroke={colors[idx % colors.length]}
                fill={colors[idx % colors.length]}
                fillOpacity={0.25}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

ServiceRetentionRadar.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      service: PropTypes.string.isRequired,
      d7: PropTypes.number.isRequired,
      d14: PropTypes.number.isRequired,
      d30: PropTypes.number.isRequired,
      total_users: PropTypes.number,
      cohort_count: PropTypes.number,
    }),
  ),
};
