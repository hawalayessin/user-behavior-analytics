import { useState, useMemo, useEffect } from "react"
import { AlertCircle, RotateCcw, ChevronUp, ChevronDown, Search, Download } from "lucide-react"
import * as XLSX from "xlsx"
import AppLayout            from "../../components/layout/AppLayout"
import FilterBar            from "../../components/dashboard/FilterBar"
import KPICard              from "../../components/dashboard/KPICard"
import TrialDropoffChart    from "../../components/dashboard/TrialDropoffChart"
import SubscriptionDonutChart from "../../components/dashboard/SubscriptionDonutChart"
import EngagementHealthPanel from "../../components/dashboard/EngagementHealthPanel"
import { useTrialKPIs }     from "../../hooks/useTrialKPIs"
import { useTrialUsers }    from "../../hooks/useTrialUsers"
import {
  TrendingDown, TrendingUp, Calendar,
  AlertTriangle, Clock,
} from "lucide-react"

const TRIAL_STATUS_MAP = {
  active:    { label: "Trial Active",  bg: "bg-amber-500/20", text: "text-amber-300", border: "border-amber-500/30" },
  converted: { label: "Converted",     bg: "bg-emerald-500/20", text: "text-emerald-300", border: "border-emerald-500/30" },
  dropped:   { label: "Dropped",       bg: "bg-red-500/20",     text: "text-red-300",     border: "border-red-500/30" },
}

const ITEMS_PER_PAGE = 8

function getDateRange(daysBack) {
  const today = new Date()
  const start = new Date(today.getTime() - daysBack * 24 * 60 * 60 * 1000)
  const fmt   = (d) => d.toISOString().split("T")[0]
  return { start_date: fmt(start), end_date: fmt(today), service_id: null }
}

const KPISkeleton   = () => <div className="w-full h-32 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
const ChartSkeleton = () => <div className="w-full h-96 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
const RowSkeleton   = () => (
  <tr>
    {Array.from({ length: 7 }).map((_, i) => (
      <td key={i} className="px-6 py-4">
        <div className="h-4 bg-slate-700 animate-pulse rounded w-3/4" />
      </td>
    ))}
  </tr>
)

export default function FreeTrialBehaviorPage() {

  const [filters,        setFilters]       = useState(getDateRange(7))
  const [searchInput,    setSearchInput]   = useState("")
  const [search,         setSearch]        = useState("")
  const [statusFilter,   setStatusFilter]  = useState("")
  const [sortField,      setSortField]     = useState("trial_start_date")
  const [sortDir,        setSortDir]       = useState("desc")
  const [page,           setPage]          = useState(1)
  const [exportOpen,     setExportOpen]    = useState(false)
  const [exportLoading,  setExportLoading] = useState(false)
  const [toastMsg,       setToastMsg]      = useState(null)

  // ── Debounce search 400ms ─────────────────────────────────
  useEffect(() => {
    const t = setTimeout(() => { setSearch(searchInput); setPage(1) }, 400)
    return () => clearTimeout(t)
  }, [searchInput])

  // ── Close export dropdown on outside click ────────────────
  useEffect(() => {
    const handler = (e) => {
      if (!e.target.closest(".export-dropdown")) setExportOpen(false)
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  const {
    data:    kpiData,
    loading: kpiLoading,
    error:   kpiError,
    refetch: refetchKPIs,
  } = useTrialKPIs(filters)

  const {
    data:    trialUsersData,
    loading: trialUsersLoading,
    error:   trialUsersError,
    refetch: refetchTrialUsers,
  } = useTrialUsers({
    status:     statusFilter || undefined,
    search:     search       || undefined,
    service_id: filters.service_id || undefined,
    page,
    limit: ITEMS_PER_PAGE,
  })

  const kpis = useMemo(() => {
    if (!kpiData) return null
    return {
      total_trials:     kpiData.total_trials     ?? 0,
      conversion_rate:  kpiData.conversion_rate  ?? 0,
      avg_duration:     kpiData.avg_duration     ?? 0,
      dropoff_j3:       kpiData.dropoff_j3       ?? 0,
    }
  }, [kpiData])

  const trialUsers = trialUsersData?.data  ?? []
  const totalCount = trialUsersData?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(totalCount / ITEMS_PER_PAGE))

  const sortedTrialUsers = useMemo(() => {
    return [...trialUsers].sort((a, b) => {
      const va = a[sortField] ?? ""
      const vb = b[sortField] ?? ""
      if (va < vb) return sortDir === "asc" ? -1 :  1
      if (va > vb) return sortDir === "asc" ?  1 : -1
      return 0
    })
  }, [trialUsers, sortField, sortDir])

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

  // ── Toast ─────────────────────────────────────────────────
  const showToast = (msg) => {
    setToastMsg(msg)
    setTimeout(() => setToastMsg(null), 3500)
  }

  // ── Build rows for export ─────────────────────────────────
  const buildRows = (list) =>
    list.map((user) => {
      const cfg = TRIAL_STATUS_MAP[user.status] ?? TRIAL_STATUS_MAP.dropped
      const duration = user.trial_duration_days ?? 0
      const converted = user.status === "converted" ? "Yes" : "No"
      return {
        "Number":         user.phone_number ?? "—",
        "Service":        user.service_name || "—",
        "Trial Start":    user.trial_start_date
                            ? new Date(user.trial_start_date).toLocaleDateString("en-GB")
                            : "—",
        "Trial End":      user.trial_end_date
                            ? new Date(user.trial_end_date).toLocaleDateString("en-GB")
                            : "—",
        "Status":         cfg.label,
        "Converted":      converted,
        "Duration (days)": duration.toFixed(1),
      }
    })

  // ── Fetch ALL trial users via export=true ──────────────────
  const fetchAllTrialUsersForExport = async () => {
    setExportLoading(true)
    try {
      const params = new URLSearchParams()
      if (statusFilter)       params.append("status",     statusFilter)
      if (search)             params.append("search",     search)
      if (filters.service_id) params.append("service_id", filters.service_id)
      params.append("export", "true")

      const res  = await fetch(`/api/users/trial?${params.toString()}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      return json.data ?? []
    } catch (err) {
      showToast("❌ Export failed: " + err.message)
      return []
    } finally {
      setExportLoading(false)
    }
  }

  // ── Export CSV ────────────────────────────────────────────
  const exportCSV = async () => {
    const allUsers = await fetchAllTrialUsersForExport()
    if (!allUsers.length) return showToast("⚠️ No data to export")

    const rows    = buildRows(allUsers)
    const headers = ["Number", "Service", "Trial Start", "Trial End", "Status", "Converted", "Duration (days)"]
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
    a.download = `trial_users_export_${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast(`✅ ${allUsers.length} trial users exported to CSV`)
  }

  // ── Export Excel ──────────────────────────────────────────
  const exportExcel = async () => {
    const allUsers = await fetchAllTrialUsersForExport()
    if (!allUsers.length) return showToast("⚠️ No data to export")

    const rows = buildRows(allUsers)
    const ws   = XLSX.utils.json_to_sheet(rows)
    const wb   = XLSX.utils.book_new()
    ws["!cols"] = [
      { wch: 18 }, { wch: 16 }, { wch: 15 },
      { wch: 15 }, { wch: 15 }, { wch: 12 }, { wch: 15 },
    ]
    XLSX.utils.book_append_sheet(wb, ws, "Trial Users")
    XLSX.writeFile(wb, `trial_users_export_${new Date().toISOString().split("T")[0]}.xlsx`)
    showToast(`✅ ${allUsers.length} trial users exported to Excel`)
  }

  return (
    <AppLayout pageTitle="Free Trial Behavior">
      <div className="space-y-6">

        {/* ── Header ────────────────────────────────────────── */}
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Free Trial Behavior</h1>
          <p className="text-sm text-slate-400">Analyze user engagement during trial period and conversion metrics</p>
        </div>

        {/* ── Filter Bar ────────────────────────────────────── */}
        <FilterBar onApply={handleApplyFilters} />

        {/* ── Erreur KPIs ───────────────────────────────────── */}
        {kpiError && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">{kpiError}</p>
            <button
              onClick={refetchKPIs}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Retry
            </button>
          </div>
        )}

        {/* ── KPI Cards (2x2 Grid) ──────────────────────────── */}
        {!kpiError && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {kpiLoading
              ? Array.from({ length: 4 }).map((_, i) => <KPISkeleton key={i} />)
              : kpis ? (
                <>
                  <KPICard
                    title="Total Trials Started"
                    value={kpis.total_trials.toLocaleString()}
                    subtitle="Active and past trials"
                    icon={TrendingUp}
                    iconColor="#3B82F6"
                    iconBg="bg-blue-500/10"
                    trend={0}
                    trendLabel="stable"
                  />
                  <KPICard
                    title="Conversion Rate"
                    value={`${kpis.conversion_rate.toFixed(1)}%`}
                    subtitle="Trial → Paid conversion"
                    icon={TrendingUp}
                    iconColor={kpis.conversion_rate < 20 ? "#EF4444" : "#10B981"}
                    iconBg={kpis.conversion_rate < 20 ? "bg-red-500/10" : "bg-green-500/10"}
                    trend={kpis.conversion_rate < 20 ? -1 : 0}
                    trendLabel={kpis.conversion_rate < 20 ? "below target" : "on track"}
                    alert={kpis.conversion_rate < 20}
                  />
                  <KPICard
                    title="Avg Trial Duration"
                    value={`${kpis.avg_duration.toFixed(1)}d`}
                    subtitle="Average days in trial"
                    icon={Calendar}
                    iconColor="#8B5CF6"
                    iconBg="bg-violet-500/10"
                    trend={0}
                    trendLabel="stable"
                  />
                  <KPICard
                    title="Day 3 Drop-off Rate"
                    value={`${kpis.dropoff_j3.toFixed(0)}%`}
                    subtitle="Users who drop-off by day 3"
                    icon={AlertTriangle}
                    iconColor="#F59E0B"
                    iconBg="bg-amber-500/10"
                    trend={-1}
                    trendLabel="warning"
                    alert={kpis.dropoff_j3 > 50}
                  />
                </>
              ) : null
            }
          </div>
        )}

        {/* ── 2x2 Grid: Charts + Table ──────────────────────── */}
        {!kpiError && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Row 1: TrialDropoffChart + SubscriptionDonutChart */}
            <div>
              {kpiLoading
                ? <ChartSkeleton />
                : <TrialDropoffChart data={[
                    { label: "Day 1\n(0-24h)", value: 45, fill: "#EF4444" },
                    { label: "Day 2\n(24-48h)", value: 32, fill: "#F97316" },
                    { label: "Day 3\n(48-72h)", value: 28, fill: "#FBBF24" },
                  ]} />
              }
            </div>

            <div>
              {kpiLoading
                ? <ChartSkeleton />
                : <SubscriptionDonutChart data={[
                    { name: "Trial", value: 45, fill: "#3B82F6" },
                    { name: "Active", value: 120, fill: "#10B981" },
                    { name: "Cancelled", value: 35, fill: "#EF4444" },
                  ]} />
              }
            </div>

            {/* Row 2: EngagementHealthPanel + TrialUsersTable */}
            <div>
              {kpiLoading
                ? <ChartSkeleton />
                : <EngagementHealthPanel bars={[
                    { label: "Trial Completion", value: 42, sublabel: "completed full trial", color: "#3B82F6", target: 50 },
                    { label: "Day 1 Retention", value: 78, sublabel: "return after signup", color: "#10B981", target: 80 },
                    { label: "Day 3 Retention", value: 38, sublabel: "active at 72 hours", color: "#F59E0B", target: 50 },
                  ]} />
              }
            </div>

            <div>
              {trialUsersLoading
                ? <ChartSkeleton />
                : (
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                    <h3 className="text-lg font-bold text-slate-100">Trial Summary Stats</h3>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Total in trial:</span>
                        <span className="text-slate-100 font-medium">{trialUsers.filter(u => u.status === "active").length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Converted:</span>
                        <span className="text-emerald-400 font-medium">{trialUsers.filter(u => u.status === "converted").length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Dropped:</span>
                        <span className="text-red-400 font-medium">{trialUsers.filter(u => u.status === "dropped").length}</span>
                      </div>
                    </div>
                  </div>
                )
              }
            </div>

          </div>
        )}

        {/* ── Table Utilisateurs en essai ────────────────────── */}
        <div className="space-y-4">

          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-100">Trial Users</h2>
            <span className="text-sm text-slate-400">
              {totalCount} user{totalCount !== 1 ? "s" : ""}
            </span>
          </div>

          {/* ── Filtres table ─────────────────────────────────── */}
          <div className="flex flex-wrap items-center gap-3 p-4 bg-slate-800 border border-slate-700 rounded-lg">

            {/* Search */}
            <div className="flex-1 min-w-[200px] relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search by number..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-700 border border-slate-600 rounded text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500"
              />
            </div>

            {/* Status filter */}
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-sm text-slate-100 focus:outline-none focus:border-violet-500"
            >
              <option value="">All statuses</option>
              <option value="active">Trial Active</option>
              <option value="converted">Converted</option>
              <option value="dropped">Dropped</option>
            </select>

            {/* Export dropdown */}
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

            {/* Refresh */}
            <button
              onClick={() => { refetchTrialUsers(); refetchKPIs() }}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-300 rounded transition"
            >
              <RotateCcw size={14} /> Refresh
            </button>
          </div>

          {/* ── Erreur table ──────────────────────────────────── */}
          {trialUsersError && (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
              <p className="flex-1 text-sm text-red-200">{trialUsersError}</p>
              <button
                onClick={refetchTrialUsers}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
              >
                <RotateCcw size={14} /> Retry
              </button>
            </div>
          )}

          {/* ── Table ─────────────────────────────────────────── */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">

                <thead className="bg-slate-800 border-b border-slate-700">
                  <tr>
                    {[
                      { label: "Number",     field: "phone_number"     },
                      { label: "Service",    field: "service_name"     },
                      { label: "Trial Start", field: "trial_start_date" },
                      { label: "Trial End",  field: "trial_end_date"   },
                      { label: "Status",     field: "status"           },
                      { label: "Converted",  field: null               },
                      { label: "Duration",   field: "trial_duration_days" },
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
                  {trialUsersLoading
                    ? Array.from({ length: ITEMS_PER_PAGE }).map((_, i) => <RowSkeleton key={i} />)
                    : sortedTrialUsers.length === 0
                      ? (
                        <tr>
                          <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                            <AlertTriangle size={32} className="mx-auto mb-2 opacity-30" />
                            No trial users found
                          </td>
                        </tr>
                      )
                      : sortedTrialUsers.map((user) => {
                          const cfg = TRIAL_STATUS_MAP[user.status] ?? TRIAL_STATUS_MAP.dropped
                          const duration = user.trial_duration_days ?? 0
                          const converted = user.status === "converted" ? "Yes" : "No"
                          const convertedBg = user.status === "converted"
                            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                            : "bg-slate-700 text-slate-300 border-slate-600"
                          return (
                            <tr key={user.id} className="hover:bg-slate-800/30 transition cursor-pointer">
                              <td className="px-6 py-4 font-mono text-slate-200 text-xs">
                                {user.phone_number ?? "—"}
                              </td>
                              <td className="px-6 py-4">
                                <span className="px-2 py-0.5 bg-slate-700 text-slate-300 text-xs rounded">
                                  {user.service_name || "—"}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-slate-400 text-xs">
                                {user.trial_start_date
                                  ? new Date(user.trial_start_date).toLocaleDateString("en-GB")
                                  : "—"}
                              </td>
                              <td className="px-6 py-4 text-slate-400 text-xs">
                                {user.trial_end_date
                                  ? new Date(user.trial_end_date).toLocaleDateString("en-GB")
                                  : "—"}
                              </td>
                              <td className="px-6 py-4">
                                <span className={`inline-block px-3 py-1 rounded text-xs font-medium border ${cfg.bg} ${cfg.text} ${cfg.border}`}>
                                  {cfg.label}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <span className={`inline-block px-3 py-1 rounded text-xs font-medium border ${convertedBg}`}>
                                  {converted}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-slate-400 text-xs font-mono">
                                {duration.toFixed(1)}d
                              </td>
                            </tr>
                          )
                        })
                  }
                </tbody>
              </table>
            </div>

            {/* Pagination */}
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

      {/* ── Toast ─────────────────────────────────────────────── */}
      {toastMsg && (
        <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-600 bg-slate-800 text-sm text-slate-100 shadow-xl">
          {toastMsg}
        </div>
      )}

    </AppLayout>
  )
}
