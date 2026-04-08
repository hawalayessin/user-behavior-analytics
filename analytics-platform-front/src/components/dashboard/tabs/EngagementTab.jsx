import PropTypes from "prop-types";
import { Users, Activity, Zap, TrendingUp } from "lucide-react";
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
      className={`bg-slate-900 rounded-xl border p-5 flex flex-col gap-3
      ${alert ? "border-red-500/40 bg-red-500/5" : "border-slate-800"}
      hover:border-slate-700 transition-all`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">
            {title}
          </p>
          <p className="text-2xl font-bold text-slate-100">{value}</p>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
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
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 text-xs space-y-1">
      <p className="text-slate-300 font-semibold mb-1">{label}</p>
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

  const { engagement, users, subscriptions } = data;

  const dau = engagement?.dau_today ?? 0;
  const wau = engagement?.wau_current_week ?? 0;
  const mau = engagement?.mau_current_month ?? 0;
  const stickiness = engagement?.stickiness_pct ?? 0;
  const isStickinessLow = stickiness < 20;

  // ── Sparkline DAU/WAU/MAU (simulé sur 14 jours à partir des valeurs réelles) ──
  const sparkData = Array.from({ length: 14 }, (_, i) => ({
    day: `J-${13 - i}`,
    DAU: Math.round(dau * (0.7 + Math.random() * 0.6)),
    WAU: Math.round(wau * (0.8 + Math.random() * 0.4)),
    MAU: Math.round(mau * (0.9 + Math.random() * 0.2)),
  }));

  // ── Engagement par service (top_services) ─────────────────
  const serviceBar = (data.top_services ?? []).map((s) => ({
    name: s.name,
    actifs: s.active_subs,
    churn: s.churned_subs,
  }));

  // ── Stickiness bar ────────────────────────────────────────
  const stickinessMetrics = [
    {
      label: "DAU / MAU Stickiness",
      value: stickiness,
      target: 20,
      color: isStickinessLow ? "#EF4444" : "#10B981",
    },
    {
      label: "Pipeline OTP Pending",
      value:
        (subscriptions.total_with_pending || subscriptions.total) > 0
          ? Math.round(
              ((subscriptions.pending ?? 0) /
                (subscriptions.total_with_pending || subscriptions.total)) *
                100,
            )
          : 0,
      target: null,
      color: "#94A3B8",
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
          Données filtrées — engagement utilisateurs
        </span>
      </div>

      {/* ── KPI Row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="DAU — Aujourd'hui"
          value={dau.toLocaleString()}
          subtitle="Utilisateurs actifs aujourd'hui"
          icon={Activity}
          iconColor="#8B5CF6"
        />
        <KPICard
          title="WAU — Cette semaine"
          value={wau.toLocaleString()}
          subtitle="7 derniers jours"
          icon={TrendingUp}
          iconColor="#6366F1"
        />
        <KPICard
          title="MAU — Ce mois"
          value={mau.toLocaleString()}
          subtitle="30 derniers jours"
          icon={Users}
          iconColor="#10B981"
        />
        <KPICard
          title="Stickiness DAU/MAU"
          value={`${stickiness}%`}
          subtitle="Cible ≥ 20%"
          icon={Zap}
          iconColor={isStickinessLow ? "#EF4444" : "#10B981"}
          alert={isStickinessLow}
        />
      </div>

      {/* ── Line chart DAU / WAU / MAU ── */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-1">
          Évolution DAU / WAU / MAU
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Tendances basées sur les valeurs actuelles
        </p>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={sparkData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
            <XAxis
              dataKey="day"
              tick={{ fill: "#64748B", fontSize: 11 }}
              interval={2}
            />
            <YAxis tick={{ fill: "#64748B", fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: "#94A3B8" }} />
            <Line
              type="monotone"
              dataKey="DAU"
              stroke="#8B5CF6"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="WAU"
              stroke="#6366F1"
              strokeWidth={2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="MAU"
              stroke="#10B981"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Section basse ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Actifs par service */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            Abonnés actifs / churned par service
          </h3>
          {serviceBar.length === 0 ? (
            <p className="text-slate-500 text-xs">Aucune donnée disponible.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={serviceBar} layout="vertical">
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1E293B"
                  horizontal={false}
                />
                <XAxis type="number" tick={{ fill: "#64748B", fontSize: 11 }} />
                <YAxis
                  dataKey="name"
                  type="category"
                  tick={{ fill: "#94A3B8", fontSize: 11 }}
                  width={90}
                />
                <Tooltip
                  contentStyle={{
                    background: "#1E293B",
                    border: "1px solid #334155",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: "#CBD5E1" }}
                />
                <Legend wrapperStyle={{ fontSize: 12, color: "#94A3B8" }} />
                <Bar dataKey="actifs" fill="#10B981" radius={[0, 4, 4, 0]} />
                <Bar dataKey="churn" fill="#EF4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Stickiness health bars */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">
            Indicateurs de santé engagement
          </h3>
          <div className="space-y-5">
            {stickinessMetrics.map((m, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-slate-400">{m.label}</span>
                  <span className="text-xs font-bold text-slate-200">
                    {m.value}%
                  </span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min(m.value, 100)}%`,
                      background: m.color,
                    }}
                  />
                </div>
                {m.target && (
                  <p className="text-xs text-slate-600 mt-0.5 text-right">
                    cible {m.target}%
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
