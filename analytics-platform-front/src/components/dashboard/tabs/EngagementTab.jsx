import PropTypes from "prop-types";
import { Activity, AlertTriangle, ShieldAlert, Users } from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

// ── KPI Card ───────────────────────────────────────────────────────────────────
function KPICard({ title, value, subtitle, icon: Icon, iconColor, alert }) {
  return (
    <div
      className={`rounded-xl p-5 flex flex-col gap-3 transition-all`}
      style={{
        backgroundColor: alert
          ? "var(--color-danger-bg)"
          : "var(--color-bg-card)",
        border: `1px solid ${alert ? "var(--color-danger)" : "var(--color-border)"}`,
        boxShadow: "var(--color-card-shadow)",
      }}
    >
      <div className="flex items-start justify-between">
        <div>
          <p
            className="text-xs font-medium uppercase tracking-wide mb-1"
            style={{ color: "var(--color-text-muted)" }}
          >
            {title}
          </p>
          <p
            className="text-2xl font-bold"
            style={{ color: "var(--color-text-primary)" }}
          >
            {value}
          </p>
          {subtitle && (
            <p
              className="text-xs mt-1"
              style={{ color: "var(--color-text-muted)" }}
            >
              {subtitle}
            </p>
          )}
        </div>
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: "var(--color-bg-elevated)" }}
        >
          <Icon size={18} color={iconColor} />
        </div>
      </div>
    </div>
  );
}
KPICard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  icon: PropTypes.elementType.isRequired,
  iconColor: PropTypes.string.isRequired,
  alert: PropTypes.bool,
};

// ── Tooltip custom ─────────────────────────────────────────────────────────────
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="rounded-lg p-3 text-xs space-y-1"
      style={{
        backgroundColor: "var(--chart-tooltip-bg)",
        border: "1px solid var(--chart-tooltip-border)",
      }}
    >
      <p
        className="font-semibold mb-1"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {label}
      </p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name} :{" "}
          <span className="font-bold">{p.value.toLocaleString()}</span>
        </p>
      ))}
    </div>
  );
};
CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
  label: PropTypes.string,
};

// ── Composant principal ────────────────────────────────────────────────────────
export default function EngagementTab({ data }) {
  if (!data) return null;

  const { engagement, subscriptions } = data;

  const engagementScore = Number(engagement?.engagement_score ?? 0);
  const engagementLevel = String(engagement?.engagement_level ?? "low");
  const inactivityRate = Number(engagement?.inactivity_rate_pct ?? 0);
  const active7d = Number(engagement?.active_7d_users ?? 0);
  const atRiskUsers = Number(subscriptions?.at_risk_users ?? 0);
  const engagementTrend = Array.isArray(engagement?.trend)
    ? engagement.trend.slice(-30).map((row) => ({
        date: row.date,
        dau: Number(row.dau ?? 0),
        wau_7d_avg: Number(row.wau_7d_avg ?? 0),
      }))
    : [];

  const levelColor =
    engagementLevel === "high"
      ? "#10B981"
      : engagementLevel === "medium"
        ? "#F59E0B"
        : "#EF4444";

  // ── Engagement par service (top_services) ─────────────────
  const serviceBar = (data.top_services ?? []).map((s) => ({
    name: s.name,
    active_users: s.active_users,
    churn_rate_pct: Number(s.churn_rate_pct ?? 0),
  }));

  const healthMetrics = [
    {
      label: "Engagement Score",
      value: engagementScore,
      target: 70,
      color: levelColor,
    },
    {
      label: "Inactivity Rate (7d)",
      value: inactivityRate,
      target: 25,
      color: inactivityRate > 25 ? "#EF4444" : "#10B981",
    },
  ];

  return (
    <div className="space-y-6">
      {/* ── Badge ── */}
      <div className="flex items-center gap-2">
        <span
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full
                         bg-indigo-500/10 border border-indigo-500/20
                         text-indigo-300 text-xs font-medium"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          Filtered data - user engagement
        </span>
      </div>

      {/* ── KPI Row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Engagement Score"
          value={`${engagementScore.toFixed(1)}/100`}
          subtitle={`Level: ${engagementLevel.toUpperCase()}`}
          icon={Activity}
          iconColor={levelColor}
        />
        <KPICard
          title="Active Users (7d)"
          value={active7d.toLocaleString()}
          subtitle="Active population over 7 days"
          icon={Users}
          iconColor="#3B82F6"
        />
        <KPICard
          title="Inactivity Rate"
          value={`${inactivityRate.toFixed(1)}%`}
          subtitle="Users with no activity over 7 days"
          icon={AlertTriangle}
          iconColor={inactivityRate > 25 ? "#EF4444" : "#10B981"}
          alert={inactivityRate > 25}
        />
        <KPICard
          title="At-Risk Subscribers"
          value={atRiskUsers.toLocaleString()}
          subtitle="Subscribers at risk (billing failed)"
          icon={ShieldAlert}
          iconColor={atRiskUsers > 0 ? "#F59E0B" : "#10B981"}
        />
      </div>

      {/* ── Real engagement line chart ── */}
      <div
        className="rounded-xl p-6"
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          boxShadow: "var(--color-card-shadow)",
        }}
      >
        <h3
          className="text-sm font-semibold mb-1"
          style={{ color: "var(--color-text-primary)" }}
        >
          Engagement Trend (last 30 days)
        </h3>
        <p
          className="text-xs mb-4"
          style={{ color: "var(--color-text-muted)" }}
        >
          Real DAU data and 7-day moving average
        </p>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={engagementTrend}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
            <XAxis
              dataKey="date"
              tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
              interval={4}
              axisLine={{ stroke: "var(--chart-grid)" }}
              tickLine={{ stroke: "var(--chart-grid)" }}
            />
            <YAxis
              tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
              axisLine={{ stroke: "var(--chart-grid)" }}
              tickLine={{ stroke: "var(--chart-grid)" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => (
                <span
                  style={{ color: "var(--color-text-muted)", fontSize: 12 }}
                >
                  {value}
                </span>
              )}
            />
            <Line
              type="monotone"
              dataKey="dau"
              stroke="#8B5CF6"
              strokeWidth={2}
              dot={false}
              name="DAU"
            />
            <Line
              type="monotone"
              dataKey="wau_7d_avg"
              stroke="#10B981"
              strokeWidth={2}
              dot={false}
              name="7-day moving average"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Section basse ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Engagement by service */}
        <div
          className="rounded-xl p-6"
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
            Engagement by Service
          </h3>
          {serviceBar.length === 0 ? (
            <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              No data available.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={serviceBar} layout="vertical">
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--chart-grid)"
                  horizontal={false}
                />
                <XAxis
                  type="number"
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
                  width={90}
                  axisLine={{ stroke: "var(--chart-grid)" }}
                  tickLine={{ stroke: "var(--chart-grid)" }}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--chart-tooltip-bg)",
                    border: "1px solid var(--chart-tooltip-border)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: "var(--color-text-secondary)" }}
                />
                <Legend
                  formatter={(value) => (
                    <span
                      style={{ color: "var(--color-text-muted)", fontSize: 12 }}
                    >
                      {value}
                    </span>
                  )}
                />
                <Bar
                  dataKey="active_users"
                  name="Active users"
                  fill="#3B82F6"
                  radius={[0, 4, 4, 0]}
                />
                <Bar
                  dataKey="churn_rate_pct"
                  name="Churn rate %"
                  fill="#EF4444"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Engagement health bars */}
        <div
          className="rounded-xl p-6"
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
            Engagement Health Indicators
          </h3>
          <div className="space-y-5">
            {healthMetrics.map((m, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <span
                    className="text-xs"
                    style={{ color: "var(--color-text-muted)" }}
                  >
                    {m.label}
                  </span>
                  <span
                    className="text-xs font-bold"
                    style={{ color: "var(--color-text-secondary)" }}
                  >
                    {m.value}%
                  </span>
                </div>
                <div
                  className="h-2 rounded-full overflow-hidden"
                  style={{ backgroundColor: "var(--color-bg-elevated)" }}
                >
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min(m.value, 100)}%`,
                      background: m.color,
                    }}
                  />
                </div>
                {m.target && (
                  <p
                    className="text-xs mt-0.5 text-right"
                    style={{ color: "var(--color-text-disabled)" }}
                  >
                    Target {m.target}%
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

EngagementTab.propTypes = {
  data: PropTypes.object,
  filters: PropTypes.object,
};
