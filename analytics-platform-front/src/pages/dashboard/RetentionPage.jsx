import { useState, useEffect, useMemo } from "react"
import { AlertCircle, RotateCcw, Search, Download, ChevronDown, ChevronUp } from "lucide-react"
import * as XLSX from "xlsx"

import AppLayout from "../../components/layout/AppLayout"
import FilterBar from "../../components/dashboard/FilterBar"
import KPICard from "../../components/dashboard/KPICard"
import CohortHeatmap from "../../components/dashboard/retention/CohortHeatmap"
import RetentionCurve from "../../components/dashboard/retention/RetentionCurve"
import ServiceRetentionRadar from "../../components/dashboard/retention/ServiceRetentionRadar"
import EngagementHealthPanel from "../../components/dashboard/EngagementHealthPanel"

import { useRetentionKPIs } from "../../hooks/useRetentionKPIs"
import { useRetentionHeatmap } from "../../hooks/useRetentionHeatmap"
import { useRetentionCurve } from "../../hooks/useRetentionCurve"
import { useCohortsTable } from "../../hooks/useCohortsTable"

const KPISkeleton   = () => <div className="w-full h-32 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
const ChartSkeleton = () => <div className="w-full h-80 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
const RowSkeleton   = () => (
  <tr>
    {Array.from({ length: 8 }).map((_, i) => (
      <td key={i} className="px-6 py-4">
        <div className="h-4 bg-slate-700 animate-pulse rounded w-3/4" />
      </td>
    ))}
  </tr>
)

const HEALTH_BADGE = {
  good:     "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  warning:  "bg-yellow-500/20  text-yellow-300  border-yellow-500/30",
  critical: "bg-red-500/20     text-red-300     border-red-500/30",
}

const ITEMS_PER_PAGE = 10

function getDateRange(daysBack) {
  const today = new Date()
  const start = new Date(today.getTime() - daysBack * 24 * 60 * 60 * 1000)
  const fmt   = (d) => d.toISOString().split("T")[0]
  return { start_date: fmt(start), end_date: fmt(today), service_id: null }
}

export default function RetentionPage() {
  const [filters, setFilters]     = useState(getDateRange(90))
  const [page, setPage]          = useState(1)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch]           = useState("")
  const [sortField, setSortField]     = useState("cohort_date")
  const [sortDir, setSortDir]         = useState("desc")
  const [exportOpen, setExportOpen]   = useState(false)
  const [exportLoading, setExportLoading] = useState(false)
  const [toastMsg, setToastMsg]       = useState(null)

  useEffect(() => {
    const t = setTimeout(() => setSearch(searchInput), 400)
    return () => clearTimeout(t)
  }, [searchInput])

  const {
    data:    kpiData,
    loading: kpiLoading,
    error:   kpiError,
    refetch: refetchKPIs,
  } = useRetentionKPIs(filters)

  const {
    data:    heatmapData,
    loading: heatmapLoading,
    error:   heatmapError,
    refetch: refetchHeatmap,
  } = useRetentionHeatmap({ service_id: filters.service_id, last_n_months: 6 })

  const {
    data:    curveData,
    loading: curveLoading,
    error:   curveError,
    refetch: refetchCurve,
  } = useRetentionCurve(filters)

  const {
    data:    cohortsData,
    loading: cohortsLoading,
    error:   cohortsError,
    refetch: refetchCohorts,
  } = useCohortsTable({
    service_id: filters.service_id,
    page,
    page_size: ITEMS_PER_PAGE,
  })

  const kpis = useMemo(() => {
    if (!kpiData) return null
    return {
      avg_d7:   kpiData.avg_retention_d7 ?? 0,
      avg_d30:  kpiData.avg_retention_d30 ?? 0,
      best:     kpiData.best_cohort ?? "—",
      best_d7:  kpiData.best_cohort_d7 ?? 0,
      at_risk:  kpiData.at_risk_count ?? 0,
      total:    kpiData.total_cohorts ?? 0,
    }
  }, [kpiData])

  const cohorts = cohortsData?.data ?? []
  const totalCount = cohortsData?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(totalCount / ITEMS_PER_PAGE))

  const filteredCohorts = useMemo(() => {
    if (!search) return cohorts
    const s = search.toLowerCase()
    return cohorts.filter((c) =>
      c.cohort_date.toLowerCase().includes(s) ||
      c.service_name.toLowerCase().includes(s)
    )
  }, [cohorts, search])

  const sortedCohorts = useMemo(() => {
    return [...filteredCohorts].sort((a, b) => {
      const va = a[sortField] ?? ""
      const vb = b[sortField] ?? ""
      if (va < vb) return sortDir === "asc" ? -1 :  1
      if (va > vb) return sortDir === "asc" ?  1 : -1
      return 0
    })
  }, [filteredCohorts, sortField, sortDir])

  const toggleSort = (field) => {
    if (sortField === field) setSortDir((d) => d === "asc" ? "desc" : "asc")
    else { setSortField(field); setSortDir("desc") }
  }

  const SortIcon = ({ field }) =>
    sortField === field
      ? sortDir === "asc"
        ? <ChevronUp   size={14} className="text-violet-400" />
        : <ChevronDown size={14} className="text-violet-400" />
      : <ChevronDown size={14} className="opacity-20" />

  const handleApplyFilters = (f) => { setFilters(f); setPage(1) }

  const showToast = (msg) => {
    setToastMsg(msg)
    setTimeout(() => setToastMsg(null), 3500)
  }

  const buildRows = (list) =>
    list.map((c) => ({
      Cohort:  c.cohort_date,
      Service: c.service_name,
      Users:   c.total_users,
      "D7%":   c.retention_d7.toFixed(1),
      "D14%":  c.retention_d14.toFixed(1),
      "D30%":  c.retention_d30.toFixed(1),
      Health:  c.health,
    }))

  const exportCSV = async () => {
    const rows = buildRows(sortedCohorts)
    if (!rows.length) return showToast("⚠️ No data to export")

    const headers = ["Cohort", "Service", "Users", "D7%", "D14%", "D30%", "Health"]
    const csvContent = [
      headers,
      ...rows.map((r) => headers.map((h) => `"${String(r[h]).replace(/"/g, '""')}"`)),
    ]
      .map((row) => row.join(","))
      .join("\n")

    const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement("a")
    a.href     = url
    a.download = `cohorts_retention_${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast(`✅ ${rows.length} cohorts exported to CSV`)
  }

  const exportExcel = async () => {
    const rows = buildRows(sortedCohorts)
    if (!rows.length) return showToast("⚠️ No data to export")

    const ws   = XLSX.utils.json_to_sheet(rows)
    const wb   = XLSX.utils.book_new()
    ws["!cols"] = [
      { wch: 14 }, { wch: 18 }, { wch: 10 },
      { wch: 8 },  { wch: 8 },  { wch: 8 }, { wch: 10 },
    ]
    XLSX.utils.book_append_sheet(wb, ws, "Cohorts")
    XLSX.writeFile(wb, `cohorts_retention_${new Date().toISOString().split("T")[0]}.xlsx`)
    showToast(`✅ ${rows.length} cohorts exported to Excel`)
  }

  const radarSource = useMemo(() => {
    if (!cohorts.length || !curveData?.data?.length) return []
    const byService = new Map()
    for (const c of cohorts) {
      const key = c.service_name
      const current = byService.get(key) ?? {
        service: key,
        total_users: 0,
        cohort_count: 0,
        sum_d7: 0,
        sum_d14: 0,
        sum_d30: 0,
      }
      current.total_users  += c.total_users ?? 0
      current.cohort_count += 1
      current.sum_d7       += c.retention_d7 ?? 0
      current.sum_d14      += c.retention_d14 ?? 0
      current.sum_d30      += c.retention_d30 ?? 0
      byService.set(key, current)
    }
    return Array.from(byService.values()).map((s) => ({
      service:      s.service,
      total_users:  s.total_users,
      cohort_count: s.cohort_count,
      d7:           s.cohort_count ? s.sum_d7  / s.cohort_count : 0,
      d14:          s.cohort_count ? s.sum_d14 / s.cohort_count : 0,
      d30:          s.cohort_count ? s.sum_d30 / s.cohort_count : 0,
    }))
  }, [cohorts, curveData?.data])

  return (
    <AppLayout pageTitle="Retention Analysis">
      <div className="space-y-6">

        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Retention Analysis</h1>
          <p className="text-sm text-slate-400">
            Cohort-based retention tracking across services and periods
          </p>
        </div>

        <FilterBar onApply={handleApplyFilters} defaultPeriod="3months" />

        {(kpiError || heatmapError || curveError || cohortsError) && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">
              {kpiError || heatmapError || curveError || cohortsError}
            </p>
            <button
              onClick={() => { refetchKPIs(); refetchHeatmap(); refetchCurve(); refetchCohorts() }}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Retry
            </button>
          </div>
        )}

        {!kpiError && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {kpiLoading
              ? Array.from({ length: 4 }).map((_, i) => <KPISkeleton key={i} />)
              : kpis && (
                <>
                  <KPICard
                    title="Avg D7 Retention"
                    value={`${kpis.avg_d7.toFixed(1)}%`}
                    subtitle="Across selected cohorts"
                    icon={RotateCcw}
                    iconColor="#3B82F6"
                    iconBg="bg-blue-500/10"
                    trend={0}
                    trendLabel="stable"
                  />
                  <KPICard
                    title="Avg D30 Retention"
                    value={`${kpis.avg_d30.toFixed(1)}%`}
                    subtitle="Long-term retention"
                    icon={RotateCcw}
                    iconColor="#10B981"
                    iconBg="bg-emerald-500/10"
                    trend={0}
                    trendLabel="stable"
                  />
                  <KPICard
                    title="Best Cohort (D7)"
                    value={kpis.best}
                    subtitle={`D7: ${kpis.best_d7.toFixed(1)}%`}
                    icon={RotateCcw}
                    iconColor="#F59E0B"
                    iconBg="bg-amber-500/10"
                    trend={0}
                    trendLabel="best"
                  />
                  <KPICard
                    title="At-risk Cohorts"
                    value={kpis.at_risk}
                    subtitle={`${kpis.total} total cohorts`}
                    icon={RotateCcw}
                    iconColor="#EF4444"
                    iconBg="bg-red-500/10"
                    trend={kpis.at_risk > 0 ? -1 : 0}
                    trendLabel={kpis.at_risk > 0 ? "need attention" : "healthy"}
                    alert={kpis.at_risk > 0}
                  />
                </>
              )
            }
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            {heatmapLoading
              ? <ChartSkeleton />
              : <CohortHeatmap data={heatmapData?.data ?? []} />
            }
          </div>
          <div>
            {curveLoading
              ? <ChartSkeleton />
              : <RetentionCurve data={curveData?.data ?? []} />
            }
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ServiceRetentionRadar data={radarSource} />
          <EngagementHealthPanel
            bars={[
              {
                label: "Avg D7 Retention",
                value: Number(kpis?.avg_d7?.toFixed(1) ?? 0),
                target: 40,
                sublabel: "Target D7 ≥ 40%",
                color: "#3B82F6",
              },
              {
                label: "Avg D14 Retention",
                value: Number((kpis?.avg_d7 ?? 0) * 0.7).toFixed
                  ? Number(((kpis?.avg_d7 ?? 0) * 0.7).toFixed(1))
                  : 0,
                target: 25,
                sublabel: "Target D14 ≥ 25%",
                color: "#10B981",
              },
              {
                label: "Avg D30 Retention",
                value: Number(kpis?.avg_d30?.toFixed(1) ?? 0),
                target: 20,
                sublabel: "Target D30 ≥ 20%",
                color: "#F59E0B",
              },
            ]}
          />
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-100">Cohorts</h2>
            <span className="text-sm text-slate-400">
              {totalCount} cohort{totalCount !== 1 ? "s" : ""}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 p-4 bg-slate-800 border border-slate-700 rounded-lg">
            <div className="flex-1 min-w-[200px] relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search by cohort or service..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-700 border border-slate-600 rounded text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500"
              />
            </div>

            <div className="export-dropdown relative">
              <button
                onClick={() => !exportLoading && setExportOpen((prev) => !prev)}
                disabled={exportLoading}
                className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-300 rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {exportLoading
                  ? <RotateCcw size={14} className="animate-spin" />
                  : <Download size={14} />
                }
                {exportLoading ? "Loading..." : "Export"}
                {!exportLoading && <ChevronDown size={12} className="opacity-60" />}
              </button>

              {exportOpen && (
                <div className="absolute right-0 top-10 z-50 w-44 rounded-lg border border-slate-600 bg-slate-800 shadow-xl overflow-hidden">
                  <button
                    onClick={() => { exportCSV(); setExportOpen(false) }}
                    className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-left text-slate-300 hover:bg-slate-700 transition"
                  >
                    📄 Export CSV
                  </button>
                  <div className="border-t border-slate-700" />
                  <button
                    onClick={() => { exportExcel(); setExportOpen(false) }}
                    className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-left text-slate-300 hover:bg-slate-700 transition"
                  >
                    📊 Export Excel
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={() => { refetchCohorts(); refetchKPIs(); refetchHeatmap(); refetchCurve() }}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-300 rounded transition"
            >
              <RotateCcw size={14} /> Refresh
            </button>
          </div>

          {cohortsError && (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
              <p className="flex-1 text-sm text-red-200">{cohortsError}</p>
              <button
                onClick={refetchCohorts}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
              >
                <RotateCcw size={14} /> Retry
              </button>
            </div>
          )}

          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-800 border-b border-slate-700">
                  <tr>
                    {[
                      { label: "Cohort",  field: "cohort_date"   },
                      { label: "Service", field: "service_name"  },
                      { label: "Users",   field: "total_users"   },
                      { label: "D7%",     field: "retention_d7"  },
                      { label: "D14%",    field: "retention_d14" },
                      { label: "D30%",    field: "retention_d30" },
                      { label: "Health",  field: "health"        },
                      { label: "Trend",   field: null            },
                    ].map(({ label, field }) => (
                      <th key={label} className="px-6 py-3 text-left">
                        {field ? (
                          <button
                            onClick={() => toggleSort(field)}
                            className="flex items-center gap-2 font-semibold text-slate-300 hover:text-slate-100"
                          >
                            {label} <SortIcon field={field} />
                          </button>
                        ) : (
                          <span className="font-semibold text-slate-300">{label}</span>
                        )}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {cohortsLoading
                    ? Array.from({ length: ITEMS_PER_PAGE }).map((_, i) => <RowSkeleton key={i} />)
                    : sortedCohorts.length === 0
                      ? (
                        <tr>
                          <td colSpan={8} className="px-6 py-12 text-center text-slate-500">
                            No cohorts found
                          </td>
                        </tr>
                      )
                      : sortedCohorts.map((c) => {
                          const badge = HEALTH_BADGE[c.health] ?? HEALTH_BADGE.critical
                          return (
                            <tr key={`${c.cohort_date}-${c.service_name}`} className="hover:bg-slate-800/30 transition cursor-pointer">
                              <td className="px-6 py-4 text-slate-200 text-xs">
                                {c.cohort_date}
                              </td>
                              <td className="px-6 py-4 text-slate-300 text-xs">
                                {c.service_name}
                              </td>
                              <td className="px-6 py-4 text-slate-200 text-xs font-mono">
                                {c.total_users.toLocaleString()}
                              </td>
                              <td className="px-6 py-4 text-slate-200 text-xs">
                                {c.retention_d7.toFixed(1)}%
                              </td>
                              <td className="px-6 py-4 text-slate-200 text-xs">
                                {c.retention_d14.toFixed(1)}%
                              </td>
                              <td className="px-6 py-4 text-slate-200 text-xs">
                                {c.retention_d30.toFixed(1)}%
                              </td>
                              <td className="px-6 py-4">
                                <span className={`inline-block px-3 py-1 rounded text-xs font-medium border capitalize ${badge}`}>
                                  {c.health}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <div className="flex items-center gap-1">
                                  {[c.retention_d7, c.retention_d14, c.retention_d30].map((v, i) => (
                                    <div key={i} className="w-6 h-4 bg-slate-800 rounded-full overflow-hidden">
                                      <div
                                        className="h-full rounded-full"
                                        style={{
                                          width: `${Math.min(v, 100)}%`,
                                          backgroundColor: i === 0 ? "#3B82F6" : i === 1 ? "#10B981" : "#F59E0B",
                                        }}
                                      />
                                    </div>
                                  ))}
                                </div>
                              </td>
                            </tr>
                          )
                        })
                  }
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between px-6 py-4 border-t border-slate-700 bg-slate-800/50">
              <span className="text-sm text-slate-400">
                Page {page} / {totalPages} — {totalCount} result{totalCount !== 1 ? "s" : ""}
              </span>
              <div className="flex items-center gap-2">
                <button onClick={() => setPage(1)} disabled={page === 1}
                  className="px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
                >«</button>
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
                  className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
                >←</button>
                <span className="px-3 py-1 text-sm text-slate-100 bg-slate-700 rounded font-medium">
                  {page}
                </span>
                <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                  className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
                >→</button>
                <button onClick={() => setPage(totalPages)} disabled={page === totalPages}
                  className="px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
                >»</button>
              </div>
            </div>
          </div>
        </div>

      </div>

      {toastMsg && (
        <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-600 bg-slate-800 text-sm text-slate-100 shadow-xl">
          {toastMsg}
        </div>
      )}
    </AppLayout>
  )
}

