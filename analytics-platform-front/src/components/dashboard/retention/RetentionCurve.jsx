import PropTypes from "prop-types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

const COLORS = [
  "#6366F1",
  "#10B981",
  "#F59E0B",
  "#EC4899",
  "#22C55E",
  "#3B82F6",
];

export default function RetentionCurve({ data }) {
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
        No retention curve data
      </div>
    );
  }

  const chartData = data.map((row) => ({
    service: row.service,
    D0: row.d0,
    D7: row.d7,
    D14: row.d14,
    D30: row.d30,
  }));

  return (
    <div
      className="rounded-xl p-4 h-full flex flex-col"
      style={{
        backgroundColor: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <h3
        className="text-sm font-semibold mb-3"
        style={{ color: "var(--color-text-primary)" }}
      >
        Retention Curve by Service
      </h3>
      <div className="flex-1 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 8, right: 12, bottom: 6, left: 0 }}
          >
            <XAxis
              dataKey="service"
              tick={{ fontSize: 11, fill: "var(--chart-axis-text)" }}
              axisLine={{ stroke: "var(--chart-grid)" }}
              tickLine={{ stroke: "var(--chart-grid)" }}
              interval={0}
              angle={-20}
              textAnchor="end"
              height={48}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "var(--chart-axis-text)" }}
              tickFormatter={(v) => `${v}%`}
              domain={[0, 100]}
              axisLine={{ stroke: "var(--chart-grid)" }}
              tickLine={{ stroke: "var(--chart-grid)" }}
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
            <ReferenceLine
              y={40}
              stroke="var(--chart-grid)"
              strokeDasharray="4 4"
              label={{
                position: "right",
                value: "D7 target 40%",
                fill: "var(--chart-axis-text)",
                fontSize: 11,
              }}
            />
            {["D0", "D7", "D14", "D30"].map((key, idx) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={COLORS[idx]}
                dot={{ r: 2 }}
                activeDot={{ r: 4 }}
                strokeWidth={1.8}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

RetentionCurve.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      service: PropTypes.string.isRequired,
      d0: PropTypes.number.isRequired,
      d7: PropTypes.number.isRequired,
      d14: PropTypes.number.isRequired,
      d30: PropTypes.number.isRequired,
    }),
  ),
};
