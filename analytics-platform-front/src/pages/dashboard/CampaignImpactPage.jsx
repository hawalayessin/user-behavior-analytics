import { useEffect, useMemo, useState } from "react"
import { AlertCircle, Download, RotateCcw } from "lucide-react"

import AppLayout from "../../components/layout/AppLayout"
import FilterBar from "../../components/dashboard/FilterBar"
import KPICard from "../../components/dashboard/KPICard"

import CampaignPerformanceChart from "../../components/dashboard/campaign/CampaignPerformanceChart"
import CampaignVsOrganicChart from "../../components/dashboard/campaign/CampaignVsOrganicChart"
import ServiceCampaignComparison from "../../components/dashboard/campaign/ServiceCampaignComparison"
import CampaignFunnelChart from "../../components/dashboard/campaign/CampaignFunnelChart"

import { useCampaignKPIs } from "../../hooks/useCampaignKPIs"
import { useCampaignPerformance } from "../../hooks/useCampaignPerformance"
import { useCampaignComparison } from "../../hooks/useCampaignComparison"
import { useCampaignTimeline } from "../../hooks/useCampaignTimeline"

function SkeletonCard() {
  return <div className="w-full h-28 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
}

function SkeletonBlock({ h = "h-80" }) {
  return <div className={`w-full ${h} bg-slate-800 animate-pulse rounded-xl border border-slate-700`} />
}

function buildCSV(rows) {
  const headers = ["Campaign Name", "Service", "Send Date", "Target", "Subs", "Conv%", "D7%", "Health"]
  const body = rows.map((r) => ([
    r.name ?? "—",
    r.service_name ?? "—",
    r.send_date ?? "—",
    String(r.target_size ?? 0),
    String(r.total_subs ?? 0),
    String(Number(r.conv_rate ?? 0).toFixed(2)),
    String(Number(r.avg_d7 ?? 0).toFixed(2)),
    r.health ?? "—",
  ]))
  const escape = (v) => `"${String(v).replace(/"/g, '""')}"`
  return [headers, ...body].map((row) => row.map(escape).join(",")).join("\n")
}

function healthForConv(conv) {
  const v = Number(conv ?? 0)
  if (v >= 15) return { label: "good", cls: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" }
  if (v >= 8) return { label: "warning", cls: "bg-yellow-500/20  text-yellow-400  border-yellow-500/30" }
  return { label: "critical", cls: "bg-red-500/20     text-red-400     border-red-500/30" }
}

export default function CampaignImpactPage() {
  const [filters, setFilters] = useState({ start_date: null, end_date: null, service_id: null })
  const [page, setPage] = useState(1)
  const [selectedId, setSelectedId] = useState(null)
  const [toast, setToast] = useState(null)

  const { data: kpis, loading: kpisLoading, error: kpisError, refetch: refetchKPIs } = useCampaignKPIs(filters)
  const { data: perf, loading: perfLoading, error: perfError, refetch: refetchPerf } = useCampaignPerformance(filters)
  const { data: comp, loading: compLoading, error: compError, refetch: refetchComp } = useCampaignComparison(filters)
  const { data: tl, loading: tlLoading, error: tlError, refetch: refetchTl } = useCampaignTimeline(filters)

  const performanceRows = perf?.data ?? []
  const comparisonRows = comp?.data ?? []
  const timelineRows = tl?.data ?? []

  const rowsWithHealth = useMemo(() => {
    return performanceRows.map((r) => {
      const h = healthForConv(r.conv_rate)
      return { ...r, health: h.label, _healthCls: h.cls }
    })
  }, [performanceRows])

  const PAGE_SIZE = 10
  const totalPages = Math.max(1, Math.ceil(rowsWithHealth.length / PAGE_SIZE))
  const paged = rowsWithHealth.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const selectedCampaign = useMemo(() => {
    const byId = rowsWithHealth.find((r) => r.campaign_id === selectedId)
    if (byId) return byId
    const topBySubs = rowsWithHealth.slice().sort((a, b) => (b.total_subs ?? 0) - (a.total_subs ?? 0))[0]
    return topBySubs ?? null
  }, [rowsWithHealth, selectedId])

  // Default selection = top campaign (when data arrives)
  useEffect(() => {
    if (!selectedId && rowsWithHealth.length) {
      const top = rowsWithHealth.slice().sort((a, b) => (b.total_subs ?? 0) - (a.total_subs ?? 0))[0]
      if (top?.campaign_id) setSelectedId(top.campaign_id)
    }
  }, [rowsWithHealth, selectedId])

  const anyError = kpisError || perfError || compError || tlError
  const anyLoading = kpisLoading || perfLoading || compLoading || tlLoading

  const showToast = (msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3500)
  }

  const exportCSV = () => {
    const csv = buildCSV(rowsWithHealth)
    if (!csv || !rowsWithHealth.length) return showToast("⚠️ No data to export")

    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `campaign_impact_${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast(`✅ ${rowsWithHealth.length} rows exported`)
  }

  const retryAll = () => {
    refetchKPIs()
    refetchPerf()
    refetchComp()
    refetchTl()
  }

  return (
    <AppLayout pageTitle="Campaign Impact Analysis">
      <div className="space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Campaign Impact Analysis</h1>
            <p className="text-sm text-slate-400">Efficacité des campagnes SMS par service</p>
          </div>
          <button
            onClick={exportCSV}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg transition"
          >
            <Download size={14} />
            Export CSV
          </button>
        </div>

        <FilterBar onApply={(f) => { setFilters(f); setPage(1) }} />

        {anyError && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">{anyError}</p>
            <button
              onClick={retryAll}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Retry
            </button>
          </div>
        )}

        {/* KPI row */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {anyLoading ? (
            Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)
          ) : (
            <>
              <KPICard
                title="Total Campaigns"
                value={(kpis?.total_campaigns ?? 0).toLocaleString()}
                subtitle="Campaigns in range"
                icon={RotateCcw}
                iconColor="#6366F1"
                iconBg="bg-violet-500/10"
                trend={0}
                trendLabel="stable"
              />
              <KPICard
                title="Total Subs"
                value={(kpis?.total_subs_from_campaigns ?? 0).toLocaleString()}
                subtitle="From campaign subscriptions"
                icon={RotateCcw}
                iconColor="#10B981"
                iconBg="bg-emerald-500/10"
                trend={0}
                trendLabel="stable"
              />
              <KPICard
                title="Avg Conv Rate"
                value={`${Number(kpis?.avg_conversion_rate ?? 0).toFixed(2)}%`}
                subtitle="Avg subs / targets"
                icon={RotateCcw}
                iconColor="#3B82F6"
                iconBg="bg-blue-500/10"
                trend={0}
                trendLabel="stable"
              />
              <KPICard
                title="Avg D7 Retention"
                value={`${Number(kpis?.avg_retention_d7 ?? 0).toFixed(2)}%`}
                subtitle="Cohorts joined by month"
                icon={RotateCcw}
                iconColor="#F59E0B"
                iconBg="bg-amber-500/10"
                trend={0}
                trendLabel="stable"
              />
              <KPICard
                title="Top Campaign"
                value={kpis?.top_campaign_name ?? "—"}
                subtitle={`${(kpis?.top_campaign_subs ?? 0).toLocaleString()} subs`}
                icon={RotateCcw}
                iconColor="#EF4444"
                iconBg="bg-red-500/10"
                trend={0}
                trendLabel="top"
              />
            </>
          )}
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {perfLoading ? <SkeletonBlock /> : <CampaignPerformanceChart data={rowsWithHealth} />}
          {tlLoading ? <SkeletonBlock /> : <CampaignVsOrganicChart data={timelineRows} />}
        </div>

        {/* Comparison + Funnel */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {compLoading ? <SkeletonBlock /> : <ServiceCampaignComparison data={comparisonRows} />}
          {perfLoading ? <SkeletonBlock /> : <CampaignFunnelChart campaign={selectedCampaign} />}
        </div>

        {/* Details table */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-100">Campaign Details</h3>
              <p className="text-sm text-slate-400">Click a row to update funnel</p>
            </div>
            <span className="text-sm text-slate-400">
              {rowsWithHealth.length} campaign{rowsWithHealth.length !== 1 ? "s" : ""}
            </span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-900/40">
            <table className="w-full text-sm">
              <thead className="bg-slate-800 border-b border-slate-700">
                <tr>
                  {["Name", "Date", "Service", "Ciblés", "Subs", "Conv%", "D7%", "Health"].map((h) => (
                    <th key={h} className="px-5 py-3 text-left text-slate-300 font-semibold">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {perfLoading ? (
                  Array.from({ length: PAGE_SIZE }).map((_, i) => (
                    <tr key={i}>
                      <td colSpan={8} className="px-5 py-4">
                        <div className="h-4 w-2/3 bg-slate-700 animate-pulse rounded" />
                      </td>
                    </tr>
                  ))
                ) : paged.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-10 text-center text-slate-500">
                      No campaigns found
                    </td>
                  </tr>
                ) : (
                  paged.map((r) => (
                    <tr
                      key={r.campaign_id}
                      className={`hover:bg-slate-800/30 transition cursor-pointer ${
                        selectedId === r.campaign_id ? "bg-violet-500/10" : ""
                      }`}
                      onClick={() => setSelectedId(r.campaign_id)}
                    >
                      <td className="px-5 py-4 text-slate-100 font-medium">{r.name}</td>
                      <td className="px-5 py-4 text-slate-400 text-xs">
                        {r.send_date ? new Date(r.send_date).toLocaleDateString("en-GB") : "—"}
                      </td>
                      <td className="px-5 py-4 text-slate-300 text-xs">{r.service_name}</td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{(r.target_size ?? 0).toLocaleString()}</td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{(r.total_subs ?? 0).toLocaleString()}</td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{Number(r.conv_rate ?? 0).toFixed(2)}%</td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{Number(r.avg_d7 ?? 0).toFixed(2)}%</td>
                      <td className="px-5 py-4">
                        <span className={`inline-block px-3 py-1 rounded text-xs font-medium border capitalize ${r._healthCls}`}>
                          {r.health}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-400">
              Page {page} / {totalPages}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(1)}
                disabled={page === 1}
                className="px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                «
              </button>
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                ←
              </button>
              <span className="px-3 py-1 text-sm text-slate-100 bg-slate-700 rounded font-medium">{page}</span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                →
              </button>
              <button
                onClick={() => setPage(totalPages)}
                disabled={page === totalPages}
                className="px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                »
              </button>
            </div>
          </div>
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-600 bg-slate-800 text-sm text-slate-100 shadow-xl">
          {toast}
        </div>
      )}
    </AppLayout>
  )
}

