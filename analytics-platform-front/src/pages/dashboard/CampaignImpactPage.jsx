import { useEffect, useMemo, useState } from "react"
import { AlertCircle, Download, RotateCcw } from "lucide-react"

import AppLayout from "../../components/layout/AppLayout"
import FilterBar from "../../components/dashboard/FilterBar"
import KPICard from "../../components/dashboard/KPICard"

// Use new dashboard hook instead of multiple hooks
import { useCampaignImpactDashboard, useCampaignList } from "../../hooks/useCampaignImpactDashboard"
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters"

function SkeletonCard() {
  return <div className="w-full h-28 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
}

function SkeletonBlock({ h = "h-80" }) {
  return <div className={`w-full ${h} bg-slate-800 animate-pulse rounded-xl border border-slate-700`} />
}

export default function CampaignImpactPage() {
  const [filters, setFilters] = useState(DEFAULT_ANALYTICS_FILTERS)
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState(null)
  const [typeFilter, setTypeFilter] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [toast, setToast] = useState(null)

  // Use new dashboard hook with filters (single endpoint, cached)
  const { data: dashboard, isLoading: dashLoading, error: dashError, refetch: refetchDashboard } = useCampaignImpactDashboard(filters)
  
  // Use campaign list for table (paginated, filtered)
  const { data: listData, isLoading: listLoading, error: listError, refetch: refetchList } = useCampaignList({
    status: statusFilter,
    campaign_type: typeFilter,
    start_date: filters?.start_date ?? null,
    end_date: filters?.end_date ?? null,
    service_id: filters?.service_id ?? null,
    page,
    limit: 10,
  })

  // Extract data from dashboard
  const kpis = dashboard?.kpis ?? {}
  const byTypeData = dashboard?.charts?.by_type ?? []
  const monthlyTrendRaw = dashboard?.charts?.monthly_trend ?? []
  const topCampaigns = dashboard?.charts?.top_campaigns ?? []

  // Aggregate monthly trend by month (sum across campaign types)
  const monthlyTrend = useMemo(() => {
    const aggregated = {}
    monthlyTrendRaw.forEach((item) => {
      if (!aggregated[item.month]) {
        aggregated[item.month] = {
          month: item.month,
          campaign_count: 0,
          targeted: 0,
          subscriptions: 0,
          first_charges: 0,
          conversion_rate: 0,
        }
      }
      aggregated[item.month].campaign_count += item.campaign_count || 0
      aggregated[item.month].targeted += item.targeted || 0
      aggregated[item.month].subscriptions += item.subscriptions || 0
      aggregated[item.month].first_charges += item.first_charges || 0
    })
    
    // Recalculate conversion rate for aggregated data
    const result = Object.values(aggregated).map((agg) => ({
      ...agg,
      conversion_rate: agg.targeted > 0 ? (agg.subscriptions / agg.targeted) * 100 : 0,
    }))
    
    return result
  }, [monthlyTrendRaw])

  // Extract data from list
  const campaignRows = listData?.campaigns ?? []
  const pageInfo = listData ? { total: listData.total, pages: listData.pages, page: listData.page } : { total: 0, pages: 0, page: 1 }

  const rowsWithHealth = useMemo(() => {
    return campaignRows.map((r) => {
      const conv = Number(r.conversion_rate ?? 0)
      let health = { label: "critical", cls: "bg-red-500/20 text-red-400 border-red-500/30" }
      if (conv >= 15) health = { label: "good", cls: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" }
      else if (conv >= 8) health = { label: "warning", cls: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" }
      return { ...r, health: health.label, _healthCls: health.cls }
    })
  }, [campaignRows])

  const selectedCampaign = useMemo(() => {
    const byId = rowsWithHealth.find((r) => r.id === selectedId)
    if (byId) return byId
    const topBySubs = rowsWithHealth.slice().sort((a, b) => (b.subscriptions_acquired ?? 0) - (a.subscriptions_acquired ?? 0))[0]
    return topBySubs ?? null
  }, [rowsWithHealth, selectedId])

  // Default selection = top campaign (when data arrives)
  useEffect(() => {
    if (!selectedId && rowsWithHealth.length) {
      const top = rowsWithHealth.slice().sort((a, b) => (b.subscriptions_acquired ?? 0) - (a.subscriptions_acquired ?? 0))[0]
      if (top?.id) setSelectedId(top.id)
    }
  }, [rowsWithHealth, selectedId])

  const anyError = dashError || listError
  const anyLoading = dashLoading || listLoading

  const showToast = (msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3500)
  }

  const exportCSV = () => {
    const headers = ["Campaign Name", "Type", "Status", "Send Date", "Target", "Subs", "Conv%", "1st Charge%", "Health"]
    const body = rowsWithHealth.map((r) => ([
      r.name ?? "—",
      r.campaign_type ?? "—",
      r.status ?? "—",
      r.send_datetime ? new Date(r.send_datetime).toLocaleDateString("en-GB") : "—",
      String(r.target_size ?? 0),
      String(r.subscriptions_acquired ?? 0),
      String(Number(r.conversion_rate ?? 0).toFixed(2)),
      String(Number(r.first_charge_rate ?? 0).toFixed(2)),
      r.health ?? "—",
    ]))
    const escape = (v) => `"${String(v).replace(/"/g, '""')}"`
    const csv = [headers, ...body].map((row) => row.map(escape).join(",")).join("\n")

    if (!csv || !rowsWithHealth.length) return showToast("No data to export")

    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `campaign_impact_${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast(`${rowsWithHealth.length} rows exported`)
  }

  const retryAll = () => {
    refetchDashboard()
    refetchList()
  }

  return (
    <AppLayout pageTitle="Campaign Impact Analysis">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Campaign Impact Analysis</h1>
          <p className="text-sm text-slate-400">Track campaign performance and subscription conversions</p>
        </div>

        <FilterBar onApply={(f) => setFilters(f)} defaultPeriod="all" />

        <div className="flex items-center justify-end">
          <button
            onClick={exportCSV}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg transition"
          >
            <Download size={14} />
            Export CSV
          </button>
        </div>

        <div className="flex gap-4">
          <select
            value={statusFilter ?? "all"}
            onChange={(e) => { setStatusFilter(e.target.value === "all" ? null : e.target.value); setPage(1) }}
            className="px-3 py-2 text-sm bg-slate-800 border border-slate-700 text-slate-200 rounded-lg"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="sent">Sent</option>
            <option value="scheduled">Scheduled</option>
          </select>
          
          <select
            value={typeFilter ?? "all"}
            onChange={(e) => { setTypeFilter(e.target.value === "all" ? null : e.target.value); setPage(1) }}
            className="px-3 py-2 text-sm bg-slate-800 border border-slate-700 text-slate-200 rounded-lg"
          >
            <option value="all">All Types</option>
            <option value="welcome">Welcome</option>
            <option value="promotion">Promotion</option>
            <option value="retention">Retention</option>
            <option value="reactivation">Reactivation</option>
          </select>
        </div>

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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {dashLoading ? (
            Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
          ) : (
            <>
              <KPICard
                title="Total Campaigns"
                value={(kpis.total_campaigns ?? 0).toLocaleString()}
                subtitle="Campaigns sent"
                icon={RotateCcw}
                iconColor="#6366F1"
                iconBg="bg-violet-500/10"
                trend={0}
                trendLabel="stable"
              />
              <KPICard
                title="Total Targeted"
                value={(kpis.total_targeted ?? 0).toLocaleString()}
                subtitle="Target audience size"
                icon={RotateCcw}
                iconColor="#10B981"
                iconBg="bg-emerald-500/10"
                trend={0}
                trendLabel="stable"
              />
              <KPICard
                title="Subscriptions"
                value={(kpis.total_subscriptions ?? 0).toLocaleString()}
                subtitle="From campaigns"
                icon={RotateCcw}
                iconColor="#3B82F6"
                iconBg="bg-blue-500/10"
                trend={0}
                trendLabel="stable"
              />
              <KPICard
                title="Conversion Rate"
                value={`${Number(kpis.conversion_rate ?? 0).toFixed(2)}%`}
                subtitle="Subs / Target"
                icon={RotateCcw}
                iconColor="#F59E0B"
                iconBg="bg-amber-500/10"
                trend={0}
                trendLabel="stable"
              />
            </>
          )}
        </div>

        {/* Charts row - Type breakdown and monthly trend */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {dashLoading ? (
            <SkeletonBlock />
          ) : (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
              <h3 className="text-lg font-bold text-slate-100 mb-4">Impact by Type</h3>
              <div className="space-y-2">
                {byTypeData.map((item) => (
                  <div key={item.type} className="flex items-center justify-between p-3 bg-slate-900/50 rounded border border-slate-700/30">
                    <div>
                      <p className="font-medium text-slate-200 capitalize">{item.type}</p>
                      <p className="text-xs text-slate-400">{item.campaign_count} campaign(s)</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-slate-100">{Number(item.conversion_rate ?? 0).toFixed(2)}%</p>
                      <p className="text-xs text-slate-400">{(item.subscriptions ?? 0).toLocaleString()} subs</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {dashLoading ? (
            <SkeletonBlock />
          ) : (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
              <h3 className="text-lg font-bold text-slate-100 mb-4">Monthly Trend</h3>
              <div className="space-y-2">
                {monthlyTrend.slice(0, 5).map((item) => (
                  <div key={item.month} className="flex items-center justify-between p-3 bg-slate-900/50 rounded border border-slate-700/30">
                    <div>
                      <p className="font-medium text-slate-200">{item.month}</p>
                      <p className="text-xs text-slate-400">{item.campaign_count} campaigns</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-slate-100">{Number(item.conversion_rate ?? 0).toFixed(2)}%</p>
                      <p className="text-xs text-slate-400">{(item.subscriptions ?? 0).toLocaleString()} subs</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Top Campaigns */}
        {!dashLoading && topCampaigns.length > 0 && (
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
            <h3 className="text-lg font-bold text-slate-100 mb-4">Top Campaigns</h3>
            <div className="space-y-2">
              {topCampaigns.map((item, idx) => (
                <div key={item.id} className="flex items-center gap-4 p-3 bg-slate-900/50 rounded border border-slate-700/30">
                  <span className="w-8 h-8 flex items-center justify-center bg-slate-700 rounded-full text-slate-200 font-bold">
                    #{idx + 1}
                  </span>
                  <div className="flex-1">
                    <p className="font-medium text-slate-200">{item.name}</p>
                    <p className="text-xs text-slate-400">{item.type}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-slate-100">{Number(item.conversion_rate ?? 0).toFixed(2)}%</p>
                    <p className="text-xs text-slate-400">{(item.subscriptions ?? 0).toLocaleString()} subs</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Campaign Details Table */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-100">Campaign Details</h3>
              <p className="text-sm text-slate-400">Filterable campaign list with metrics</p>
            </div>
            <span className="text-sm text-slate-400">
              {pageInfo.total} campaign{pageInfo.total !== 1 ? "s" : ""}
            </span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-900/40">
            <table className="w-full text-sm">
              <thead className="bg-slate-800 border-b border-slate-700">
                <tr>
                  {["Name", "Type", "Status", "Date", "Target", "Subs", "Conv%", "1st Charge%", "Health"].map((h) => (
                    <th key={h} className="px-5 py-3 text-left text-slate-300 font-semibold">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {listLoading ? (
                  Array.from({ length: 10 }).map((_, i) => (
                    <tr key={i}>
                      <td colSpan={9} className="px-5 py-4">
                        <div className="h-4 w-2/3 bg-slate-700 animate-pulse rounded" />
                      </td>
                    </tr>
                  ))
                ) : rowsWithHealth.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-6 py-10 text-center text-slate-500">
                      No campaigns found
                    </td>
                  </tr>
                ) : (
                  rowsWithHealth.map((r) => (
                    <tr
                      key={r.id}
                      className={`hover:bg-slate-800/30 transition cursor-pointer ${
                        selectedId === r.id ? "bg-violet-500/10" : ""
                      }`}
                      onClick={() => setSelectedId(r.id)}
                    >
                      <td className="px-5 py-4 text-slate-100 font-medium">{r.name}</td>
                      <td className="px-5 py-4 text-slate-300 text-xs capitalize">{r.campaign_type}</td>
                      <td className="px-5 py-4 text-slate-300 text-xs capitalize">{r.status}</td>
                      <td className="px-5 py-4 text-slate-400 text-xs">
                        {r.send_datetime ? new Date(r.send_datetime).toLocaleDateString("en-GB") : "—"}
                      </td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{(r.target_size ?? 0).toLocaleString()}</td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{(r.subscriptions_acquired ?? 0).toLocaleString()}</td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{Number(r.conversion_rate ?? 0).toFixed(2)}%</td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">{Number(r.first_charge_rate ?? 0).toFixed(2)}%</td>
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
              Page {pageInfo.page} / {pageInfo.pages}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(1)}
                disabled={pageInfo.page === 1}
                className="px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                «
              </button>
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={pageInfo.page === 1}
                className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                ←
              </button>
              <span className="px-3 py-1 text-sm text-slate-100 bg-slate-700 rounded font-medium">{pageInfo.page}</span>
              <button
                onClick={() => setPage((p) => Math.min(pageInfo.pages, p + 1))}
                disabled={pageInfo.page === pageInfo.pages}
                className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                →
              </button>
              <button
                onClick={() => setPage(pageInfo.pages)}
                disabled={pageInfo.page === pageInfo.pages}
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

