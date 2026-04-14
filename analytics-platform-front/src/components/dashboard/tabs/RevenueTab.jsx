import PropTypes from "prop-types";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import SubscriptionDonutChart from "../SubscriptionDonutChart";
import NRRCard from "../../nrr/NRRCard";
import { useDashboardMetrics } from "../../../hooks/useDashboardMetrics";

const TOOLTIP_STYLE = {
  contentStyle: {
    backgroundColor: "var(--chart-tooltip-bg)",
    border: "1px solid var(--chart-tooltip-border)",
    borderRadius: 8,
    color: "var(--color-text-primary)",
  },
  labelStyle: { color: "var(--color-text-secondary)" },
  itemStyle: { color: "var(--color-text-muted)" },
};

const SERVICE_COLORS = [
  "#22C55E",
  "#06B6D4",
  "#3B82F6",
  "#8B5CF6",
  "#F59E0B",
  "#EF4444",
  "#EC4899",
  "#84CC16",
];

export default function RevenueTab({ data, nrr, nrrLoading, nrrError }) {
  const metrics = useDashboardMetrics(data);
  if (!metrics) return null;

  const { revenue, subscriptions } = data;

  const billingData = [
    {
      label: "Facturation",
      success: revenue.billing_success,
      failed: revenue.billing_failed,
    },
  ];

  const topServices = Array.isArray(data.top_services) ? data.top_services : [];
  const totalServiceSubs = topServices.reduce(
    (acc, s) => acc + Number(s.total ?? 0),
    0,
  );

  const revenueByServiceData = topServices
    .slice(0, 8)
    .map((service) => {
      const explicitRevenue = Number(
        service.revenue ?? service.total_revenue ?? service.revenue_total ?? 0,
      );

      // Fallback: proportional estimate when backend doesn't expose service-level revenue.
      const estimatedRevenue =
        explicitRevenue > 0
          ? explicitRevenue
          : totalServiceSubs > 0
            ? (Number(service.total ?? 0) / totalServiceSubs) *
              Number(revenue.total_revenue ?? 0)
            : 0;

      return {
        service: service.name,
        revenue: Number(estimatedRevenue.toFixed(2)),
      };
    })
    .sort((a, b) => b.revenue - a.revenue);

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4">
        {[
          {
            label: "ARPU",
            value: `${revenue.arpu_current_month ?? 0} DT`,
            color: "text-violet-400",
          },
          {
            label: "MRR",
            value: `${revenue.mrr ?? 0} DT`,
            color: "text-emerald-400",
          },
          {
            label: "Successful Payments",
            value: revenue.billing_success.toLocaleString(),
            color: "text-emerald-400",
          },
          {
            label: "Failed Payments",
            value: revenue.billing_failed.toLocaleString(),
            color: "text-red-400",
          },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="rounded-xl p-5"
            style={{
              backgroundColor: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              boxShadow: "var(--color-card-shadow)",
            }}
          >
            <p
              className="text-xs mb-1"
              style={{ color: "var(--color-text-muted)" }}
            >
              {kpi.label}
            </p>
            <p className={`text-xl font-bold ${kpi.color}`}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Donut + Billing bar */}
      <div className="flex gap-4">
        <SubscriptionDonutChart
          data={metrics.subscriptionPieData}
          total={subscriptions.total}
        />

        <div
          className="rounded-xl p-5 flex-1"
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
            Billing — Success vs Failed
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={billingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis
                dataKey="label"
                tick={{ fill: "var(--chart-axis-text)", fontSize: 12 }}
                axisLine={{ stroke: "var(--chart-grid)" }}
                tickLine={{ stroke: "var(--chart-grid)" }}
              />
              <YAxis
                tick={{ fill: "var(--chart-axis-text)", fontSize: 12 }}
                axisLine={{ stroke: "var(--chart-grid)" }}
                tickLine={{ stroke: "var(--chart-grid)" }}
              />
              <Tooltip {...TOOLTIP_STYLE} />
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
                dataKey="success"
                name="Success"
                fill="#10B981"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="failed"
                name="Failed"
                fill="#EF4444"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* NRR (sous Subscription Status Breakdown + Billing) */}
      <div
        className="rounded-xl p-5"
        style={{
          backgroundColor: "var(--color-bg-card)",
          border: "1px solid var(--color-border)",
          boxShadow: "var(--color-card-shadow)",
        }}
      >
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h3
              className="text-sm font-semibold mb-1"
              style={{ color: "var(--color-text-primary)" }}
            >
              Revenue by Service
            </h3>
            <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
              Distribution of revenue contribution across top services.
            </p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300">
            {revenueByServiceData.length} services
          </span>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={revenueByServiceData}
            margin={{ top: 8, right: 10, left: 8, bottom: 24 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
            <XAxis
              dataKey="service"
              tick={{ fill: "var(--chart-axis-text)", fontSize: 11 }}
              interval={0}
              angle={-18}
              textAnchor="end"
              height={64}
              axisLine={{ stroke: "var(--chart-grid)" }}
              tickLine={{ stroke: "var(--chart-grid)" }}
            />
            <YAxis
              tick={{ fill: "var(--chart-axis-text)", fontSize: 12 }}
              tickFormatter={(v) => `${Math.round(v).toLocaleString()} DT`}
              axisLine={{ stroke: "var(--chart-grid)" }}
              tickLine={{ stroke: "var(--chart-grid)" }}
            />
            <Tooltip
              {...TOOLTIP_STYLE}
              cursor={{ fill: "rgba(148,163,184,0.08)" }}
              formatter={(value) => [
                `${Number(value).toLocaleString()} DT`,
                "Revenue",
              ]}
            />
            <Bar dataKey="revenue" name="Revenue" radius={[4, 4, 0, 0]}>
              {revenueByServiceData.map((entry, index) => (
                <Cell
                  key={`${entry.service}-${index}`}
                  fill={SERVICE_COLORS[index % SERVICE_COLORS.length]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="w-full">
        <NRRCard
          data={nrr}
          loading={nrrLoading}
          error={nrrError}
          size="expanded"
        />
      </div>
    </div>
  );
}

RevenueTab.propTypes = {
  data: PropTypes.object.isRequired,
  filters: PropTypes.object.isRequired,
  nrr: PropTypes.object,
  nrrLoading: PropTypes.bool,
  nrrError: PropTypes.string,
};
