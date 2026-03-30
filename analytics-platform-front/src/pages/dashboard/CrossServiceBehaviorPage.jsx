import { useMemo, useState } from "react"
import {
  AlertCircle,
  RotateCcw,
  Users,
  Trophy,
  Shield,
  DollarSign,
  ArrowRight,
  Lightbulb,
  GitBranch,
  Package,
  Target,
  Sparkles,
} from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts"

import AppLayout from "../../components/layout/AppLayout"
import KPICard from "../../components/dashboard/KPICard"
import FilterBar from "../../components/dashboard/FilterBar"
import { useCrossService } from "../../hooks/useCrossService"
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters"

/* ───────── helpers ───────── */

function SkeletonCard() {
  return <div className="w-full h-28 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
}

function SkeletonBlock({ h = "h-80" }) {
  return <div className={`w-full ${h} bg-slate-800 animate-pulse rounded-xl border border-slate-700`} />
}

/* ───── color map for heatmap cells ───── */
function heatColor(rate) {
  if (rate >= 25) return "bg-indigo-500 text-white"
  if (rate >= 15) return "bg-indigo-500/70 text-white"
  if (rate >= 10) return "bg-indigo-500/40 text-slate-100"
  if (rate >= 5) return "bg-indigo-500/20 text-slate-200"
  if (rate > 0) return "bg-indigo-500/10 text-slate-300"
  return "bg-slate-800/50 text-slate-500"
}

/* ───── bar chart gradient colors ───── */
const BAR_COLORS = ["#6366f1", "#818cf8", "#a78bfa", "#c084fc"]

/* ───── custom tooltip for bar chart ───── */
function DistributionTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 shadow-xl">
      <p className="text-sm font-semibold text-slate-100">
        {d.nb_services} service{d.nb_services > 1 ? "s" : ""}
      </p>
      <p className="text-xs text-slate-400 mt-1">
        {d.user_count.toLocaleString()} users ({d.percentage}%)
      </p>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════
   MAIN PAGE COMPONENT
   ═══════════════════════════════════════════════════════════════ */
export default function CrossServiceBehaviorPage() {
  const [filters, setFilters] = useState(DEFAULT_ANALYTICS_FILTERS)

  const {
    overview,
    coSubscriptions,
    migrations,
    distribution,
    loading,
    error,
    refetch,
  } = useCrossService(filters)

  /* ── derive unique services list for heatmap axis ── */
  const serviceNames = useMemo(() => {
    if (!coSubscriptions?.matrix?.length) return []
    const set = new Set()
    coSubscriptions.matrix.forEach((r) => {
      set.add(r.service_a)
      set.add(r.service_b)
    })
    return Array.from(set).sort()
  }, [coSubscriptions])

  /* ── lookup map: (A,B) → rate ── */
  const rateMap = useMemo(() => {
    const m = {}
    if (!coSubscriptions?.matrix) return m
    coSubscriptions.matrix.forEach((r) => {
      m[`${r.service_a}__${r.service_b}`] = r.rate
    })
    return m
  }, [coSubscriptions])

  /* ── build recommendations from actual data ── */
  const recommendations = useMemo(() => {
    const recs = []

    // Rec 1 — bundle from top combo
    if (overview?.top_combo?.count > 0) {
      const { service_a, service_b, count } = overview.top_combo
      recs.push({
        icon: Package,
        title: "Bundle Suggestion",
        color: "text-emerald-400",
        border: "border-emerald-500/30",
        bg: "bg-emerald-500/5",
        text: `${service_a} + ${service_b} — ${count} users already subscribe to both. Consider offering a bundle discount of -20% to drive cross-adoption.`,
      })
    } else {
      recs.push({
        icon: Package,
        title: "Bundle Suggestion",
        color: "text-emerald-400",
        border: "border-emerald-500/30",
        bg: "bg-emerald-500/5",
        text: "Identify top service pairs from co-subscription data and offer bundle pricing to increase multi-service adoption.",
      })
    }

    // Rec 2 — re-engagement from top migration
    if (migrations?.migrations?.length > 0) {
      const top = migrations.migrations[0]
      recs.push({
        icon: Target,
        title: "Re-engagement Opportunity",
        color: "text-amber-400",
        border: "border-amber-500/30",
        bg: "bg-amber-500/5",
        text: `${top.user_count} users migrated from ${top.from_service} → ${top.to_service}. Target ${top.from_service} churned users with a ${top.to_service} trial campaign.`,
      })
    } else {
      recs.push({
        icon: Target,
        title: "Re-engagement Opportunity",
        color: "text-amber-400",
        border: "border-amber-500/30",
        bg: "bg-amber-500/5",
        text: "Analyse migration paths to identify re-engagement opportunities for churned users across services.",
      })
    }

    // Rec 3 — algorithmic / retention comparison
    recs.push({
      icon: Sparkles,
      title: "Algorithmic Insight",
      color: "text-violet-400",
      border: "border-violet-500/30",
      bg: "bg-violet-500/5",
      text: overview
        ? `Multi-service users show ${overview.cross_retention_rate}% retention vs ${overview.mono_retention_rate}% for mono-service users. Encouraging cross-service adoption could reduce churn significantly.`
        : "Multi-service users typically show higher retention. Collaborative filtering can recommend new services based on usage patterns.",
    })

    return recs
  }, [overview, migrations])

  return (
    <AppLayout pageTitle="Cross-Service Behavior">
      <div className="space-y-6">
        {/* ── Page Header ── */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">
              Cross-Service Behavior
            </h1>
            <p className="text-sm text-slate-400">
              Analyse multi-service adoption, migration paths and co-subscription patterns
            </p>
          </div>
          <button
            onClick={refetch}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg transition"
          >
            <RotateCcw size={14} />
            Refresh
          </button>
        </div>

        {/* ── Filter Bar ── */}
        <FilterBar onApply={setFilters} defaultPeriod="all" />

        {/* ── Error Banner ── */}
        {error && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">{error}</p>
            <button
              onClick={refetch}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Retry
            </button>
          </div>
        )}

        {/* ═══════════════════════════════════════════════
            SECTION 1 — Overview KPIs
           ═══════════════════════════════════════════════ */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {loading ? (
            Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
          ) : (
            <>
              <KPICard
                title="Multi-Service Users"
                value={
                  overview
                    ? `${(overview.multi_service_users ?? 0).toLocaleString()}`
                    : "—"
                }
                subtitle={
                  overview
                    ? `${overview.multi_service_rate ?? 0}% of total users`
                    : "Loading…"
                }
                icon={Users}
                iconColor="#6366F1"
                iconBg="bg-indigo-500/10"
                trend={0}
                trendLabel="users with 2+ services"
              />
              <KPICard
                title="Top Combo"
                value={
                  overview?.top_combo
                    ? `${overview.top_combo.service_a} + ${overview.top_combo.service_b}`
                    : "—"
                }
                subtitle={
                  overview?.top_combo
                    ? `${overview.top_combo.count.toLocaleString()} users`
                    : "Loading…"
                }
                icon={Trophy}
                iconColor="#F59E0B"
                iconBg="bg-amber-500/10"
                trend={0}
                trendLabel="most popular pair"
              />
              <KPICard
                title="Cross-Service Retention"
                value={
                  overview
                    ? `${overview.cross_retention_rate ?? 0}%`
                    : "—"
                }
                subtitle={
                  overview
                    ? `vs ${overview.mono_retention_rate ?? 0}% mono-service`
                    : "Loading…"
                }
                subtitleColor={
                  overview && overview.cross_retention_rate > overview.mono_retention_rate
                    ? "text-emerald-400"
                    : "text-slate-500"
                }
                icon={Shield}
                iconColor="#10B981"
                iconBg="bg-emerald-500/10"
                trend={0}
                trendLabel="D30 retention"
              />
              <KPICard
                title="ARPU Multi-Service"
                value={
                  overview
                    ? `${(overview.arpu_multi ?? 0).toFixed(2)} TND`
                    : "—"
                }
                subtitle={
                  overview
                    ? `vs ${(overview.arpu_mono ?? 0).toFixed(2)} TND mono`
                    : "Loading…"
                }
                icon={DollarSign}
                iconColor="#3B82F6"
                iconBg="bg-blue-500/10"
                trend={0}
                trendLabel="avg revenue per user"
              />
            </>
          )}
        </div>

        {/* ═══════════════════════════════════════════════
            SECTION 2 — Co-Subscription Heatmap
           ═══════════════════════════════════════════════ */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100">
              Co-Subscription Heatmap
            </h3>
            <p className="text-sm text-slate-400">
              Which services are used together? Percentage of row-service users who also subscribe to column-service.
            </p>
          </div>

          {loading ? (
            <SkeletonBlock h="h-64" />
          ) : serviceNames.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              No co-subscription data available
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-slate-400 font-semibold bg-slate-900/50 rounded-tl-lg">
                      Service ↓ / →
                    </th>
                    {serviceNames.map((name) => (
                      <th
                        key={name}
                        className="px-4 py-3 text-center text-slate-300 font-semibold bg-slate-900/50 text-xs"
                      >
                        {name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {serviceNames.map((rowService) => (
                    <tr key={rowService} className="border-t border-slate-700/30">
                      <td className="px-4 py-3 text-slate-200 font-medium whitespace-nowrap bg-slate-900/30">
                        {rowService}
                      </td>
                      {serviceNames.map((colService) => {
                        if (rowService === colService) {
                          return (
                            <td
                              key={colService}
                              className="px-4 py-3 text-center bg-slate-700/30 text-slate-600 text-xs"
                            >
                              —
                            </td>
                          )
                        }
                        const rate =
                          rateMap[`${rowService}__${colService}`] ?? 0
                        return (
                          <td
                            key={colService}
                            className={`px-4 py-3 text-center text-xs font-mono font-semibold rounded transition-colors ${heatColor(
                              rate
                            )}`}
                            title={`${rate}% of ${rowService} users also use ${colService}`}
                          >
                            {rate > 0 ? `${rate}%` : "—"}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* ═══════════════════════════════════════════════
            SECTION 3 + 4 — Two-column: Migrations + Distribution
           ═══════════════════════════════════════════════ */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* ── Migration Paths ── */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
            <div>
              <h3 className="text-lg font-bold text-slate-100">
                Migration Paths
              </h3>
              <p className="text-sm text-slate-400">
                User migration flows between services (ended service A → started service B)
              </p>
            </div>

            {loading ? (
              <SkeletonBlock h="h-64" />
            ) : !migrations?.migrations?.length ? (
              <div className="text-center py-12 text-slate-500">
                No migration data available
              </div>
            ) : (
              <div className="space-y-3">
                {migrations.migrations.map((m, i) => (
                  <div
                    key={`${m.from_service}-${m.to_service}`}
                    className="flex items-center gap-3 px-4 py-3 bg-slate-900/40 border border-slate-700/40 rounded-lg hover:border-slate-600 transition"
                  >
                    {/* Rank */}
                    <span className="flex-shrink-0 w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold">
                      {i + 1}
                    </span>

                    {/* From */}
                    <span className="text-sm font-medium text-slate-200 truncate min-w-0">
                      {m.from_service}
                    </span>

                    {/* Arrow */}
                    <ArrowRight size={16} className="flex-shrink-0 text-indigo-400" />

                    {/* To */}
                    <span className="text-sm font-medium text-slate-200 truncate min-w-0">
                      {m.to_service}
                    </span>

                    {/* Stats */}
                    <div className="ml-auto flex items-center gap-3 flex-shrink-0">
                      <span className="text-sm font-mono font-semibold text-indigo-300">
                        {m.user_count.toLocaleString()}
                      </span>
                      <span className="text-xs text-slate-500">
                        ({m.migration_rate}%)
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ── Service Distribution Bar Chart ── */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
            <div>
              <h3 className="text-lg font-bold text-slate-100">
                Service Distribution
              </h3>
              <p className="text-sm text-slate-400">
                How many services does a user subscribe to?
              </p>
            </div>

            {loading ? (
              <SkeletonBlock h="h-64" />
            ) : !distribution?.distribution?.length ? (
              <div className="text-center py-12 text-slate-500">
                No distribution data available
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart
                  data={distribution.distribution}
                  margin={{ top: 20, right: 20, bottom: 20, left: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    dataKey="nb_services"
                    tick={{ fill: "#94a3b8", fontSize: 12 }}
                    tickFormatter={(v) => `${v} service${v > 1 ? "s" : ""}`}
                    axisLine={{ stroke: "#475569" }}
                  />
                  <YAxis
                    tick={{ fill: "#94a3b8", fontSize: 12 }}
                    axisLine={{ stroke: "#475569" }}
                  />
                  <Tooltip content={<DistributionTooltip />} cursor={{ fill: "rgba(99,102,241,0.08)" }} />
                  <Bar dataKey="user_count" radius={[6, 6, 0, 0]} maxBarSize={60}>
                    {distribution.distribution.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={BAR_COLORS[index % BAR_COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}

            {/* labels below chart */}
            {!loading && distribution?.distribution?.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {distribution.distribution.map((d, i) => (
                  <div
                    key={d.nb_services}
                    className="text-center px-3 py-2 bg-slate-900/40 rounded-lg border border-slate-700/30"
                  >
                    <p className="text-xs text-slate-400">
                      {d.nb_services} service{d.nb_services > 1 ? "s" : ""}
                    </p>
                    <p className="text-lg font-bold text-slate-100">
                      {d.percentage}%
                    </p>
                    <p className="text-xs text-slate-500">
                      {d.user_count.toLocaleString()} users
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ═══════════════════════════════════════════════
            SECTION 5 — Recommendations Panel
           ═══════════════════════════════════════════════ */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Lightbulb size={20} className="text-amber-400" />
            <h3 className="text-lg font-bold text-slate-100">
              Cross-Service Opportunities
            </h3>
          </div>
          <p className="text-sm text-slate-400">
            Data-driven recommendations to increase multi-service adoption and revenue.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recommendations.map((rec, i) => {
              const Icon = rec.icon
              return (
                <div
                  key={i}
                  className={`rounded-xl border p-5 space-y-3 ${rec.border} ${rec.bg}`}
                >
                  <div className="flex items-center gap-2">
                    <Icon size={18} className={rec.color} />
                    <h4 className={`text-sm font-bold ${rec.color}`}>
                      {rec.title}
                    </h4>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {rec.text}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
