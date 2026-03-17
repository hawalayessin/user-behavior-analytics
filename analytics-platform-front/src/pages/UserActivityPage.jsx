import { useState, useMemo, useEffect } from "react"
import { AlertCircle, RotateCcw, ChevronUp, ChevronDown, Search, Download } from "lucide-react"
import * as XLSX from "xlsx"
import AppLayout            from "../components/layout/AppLayout"
import FilterBar            from "../components/dashboard/FilterBar"
import KPICard              from "../components/dashboard/KPICard"
import DAUTrendChart        from "../components/dashboard/userActivity/DAUTrendChart"
import ServiceActivityTable from "../components/dashboard/userActivity/ServiceActivityTable"
import UserGrowthChart      from "../components/dashboard/userActivity/UserGrowthChart"
import ActivityHeatmap      from "../components/dashboard/userActivity/ActivityHeatmap"
import { useUserActivity }  from "../hooks/useUserActivity"
import { useUsers }         from "../hooks/useUsers"
import {
  Users, TrendingUp, Calendar,
  Zap, AlertTriangle, Clock,
} from "lucide-react"

const STATUT_MAP = {
  active:   { label: "Actif",   bg: "bg-emerald-500/20", text: "text-emerald-300", border: "border-emerald-500/30" },
  trial:    { label: "Essai",   bg: "bg-blue-500/20",    text: "text-blue-300",    border: "border-blue-500/30"    },
  inactive: { label: "Inactif", bg: "bg-amber-500/20",   text: "text-amber-300",   border: "border-amber-500/30"   },
  churned:  { label: "Churné",  bg: "bg-red-500/20",     text: "text-red-300",     border: "border-red-500/30"     },
}

const ITEMS_PER_PAGE = 8

function getDefaultFilters() {
  return { start_date: null, end_date: null, service_id: null }
}

const KPISkeleton   = () => <div className="w-full h-32 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
const ChartSkeleton = () => <div className="w-full h-96 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
const RowSkeleton   = () => (
  <tr>
    {Array.from({ length: 6 }).map((_, i) => (
      <td key={i} className="px-6 py-4">
        <div className="h-4 bg-slate-700 animate-pulse rounded w-3/4" />
      </td>
    ))}
  </tr>
)

export default function UserActivityPage() {

  const [filters,      setFilters]      = useState(getDefaultFilters())
  const [searchInput,  setSearchInput]  = useState("")
  const [search,       setSearch]       = useState("")
  const [statutFilter, setStatutFilter] = useState("")
  const [sortField,    setSortField]    = useState("created_at")
  const [sortDir,      setSortDir]      = useState("desc")
  const [page,         setPage]         = useState(1)
  const [exportOpen,   setExportOpen]   = useState(false)
  const [exportLoading,setExportLoading]= useState(false)
  const [toastMsg,     setToastMsg]     = useState(null)

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
    data:    activityData,
    loading: activityLoading,
    error:   activityError,
    refetch: refetchActivity,
  } = useUserActivity(filters)

  const {
    data:    usersData,
    loading: usersLoading,
    error:   usersError,
    refetch: refetchUsers,
  } = useUsers({
    status:     statutFilter || undefined,
    search:     search       || undefined,
    service_id: filters.service_id || undefined,
    page,
    limit: ITEMS_PER_PAGE,
  })

  const kpis = useMemo(() => {
    if (!activityData?.kpis) return null
    return {
      dau_today:         activityData.kpis.dau_today         ?? 0,
      wau_current_week:  activityData.kpis.wau_current_week  ?? 0,
      mau_current_month: activityData.kpis.mau_current_month ?? 0,
      stickiness_pct:    activityData.kpis.stickiness_pct    ?? 0,
      inactive_count:    activityData.kpis.inactive_count    ?? 0,
      avg_lifetime_days: activityData.kpis.avg_lifetime_days ?? 0,
    }
  }, [activityData?.kpis])

  const users      = usersData?.data  ?? []
  const totalCount = usersData?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(totalCount / ITEMS_PER_PAGE))

  const sortedUsers = useMemo(() => {
    return [...users].sort((a, b) => {
      const va = a[sortField] ?? ""
      const vb = b[sortField] ?? ""
      if (va < vb) return sortDir === "asc" ? -1 :  1
      if (va > vb) return sortDir === "asc" ?  1 : -1
      return 0
    })
  }, [users, sortField, sortDir])

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
      const cfg = STATUT_MAP[user.status] ?? STATUT_MAP.inactive
      return {
        "Number":        user.phone_number ?? "—",
        "Status":        cfg.label,
        "Services":      (user.services ?? []).map((s) => s.name).join(" | ") || "—",
        "Registered On": user.created_at
                           ? new Date(user.created_at).toLocaleDateString("en-GB")
                           : "—",
        "Last Activity": user.last_activity_at
                           ? new Date(user.last_activity_at).toLocaleDateString("en-GB")
                           : "—",
        "Campaign":      user.campaign_name || "None",
      }
    })

  // ── Fetch ALL users via export=true ───────────────────────
  const fetchAllUsersForExport = async () => {
    setExportLoading(true)
    try {
      const params = new URLSearchParams()
      if (statutFilter)       params.append("status",     statutFilter)
      if (search)             params.append("search",     search)
      if (filters.service_id) params.append("service_id", filters.service_id)
      params.append("export", "true")   // ✅ pas de LIMIT côté backend

      const res  = await fetch(`/api/users?${params.toString()}`)
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
    const allUsers = await fetchAllUsersForExport()
    if (!allUsers.length) return showToast("⚠️ No data to export")

    const rows    = buildRows(allUsers)
    const headers = ["Number", "Status", "Services", "Registered On", "Last Activity", "Campaign"]
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
    a.download = `users_export_${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast(`✅ ${allUsers.length} users exported to CSV`)
  }

  // ── Export Excel ──────────────────────────────────────────
  const exportExcel = async () => {
    const allUsers = await fetchAllUsersForExport()
    if (!allUsers.length) return showToast("⚠️ No data to export")

    const rows = buildRows(allUsers)
    const ws   = XLSX.utils.json_to_sheet(rows)
    const wb   = XLSX.utils.book_new()
    ws["!cols"] = [
      { wch: 18 }, { wch: 12 }, { wch: 24 },
      { wch: 15 }, { wch: 15 }, { wch: 22 },
    ]
    XLSX.utils.book_append_sheet(wb, ws, "Users")
    XLSX.writeFile(wb, `users_export_${new Date().toISOString().split("T")[0]}.xlsx`)
    showToast(`✅ ${allUsers.length} users exported to Excel`)
  }

  return (
    <AppLayout pageTitle="Users Activity">
      <div className="space-y-6">

        {/* ── Header ────────────────────────────────────────── */}
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Users Activity</h1>
          <p className="text-sm text-slate-400">Comprehensive analysis of engagement and activity</p>
        </div>

        {/* ── Filter Bar ────────────────────────────────────── */}
        <FilterBar onApply={handleApplyFilters} />

        {/* ── Erreur analytics ──────────────────────────────── */}
        {activityError && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">{activityError}</p>
            <button
              onClick={refetchActivity}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Réessayer
            </button>
          </div>
        )}

        {/* ── KPI Cards ─────────────────────────────────────── */}
        {!activityError && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {activityLoading
              ? Array.from({ length: 6 }).map((_, i) => <KPISkeleton key={i} />)
              : kpis ? (
                <>
                  <KPICard title="DAU (Today)"       value={kpis.dau_today.toLocaleString()}         subtitle="Actifs aujourd'hui"            icon={Users}         iconColor="#7C3AED" iconBg="bg-purple-500/10"  trend={0} trendLabel="stable" />
                  <KPICard title="WAU (Last 7 days)"  value={kpis.wau_current_week.toLocaleString()}   subtitle="Actifs 7 derniers jours"       icon={TrendingUp}    iconColor="#3B82F6" iconBg="bg-blue-500/10"    trend={0} trendLabel="stable" />
                  <KPICard title="MAU (Last 30 days)" value={kpis.mau_current_month.toLocaleString()}  subtitle="Actifs 30 derniers jours"      icon={Calendar}      iconColor="#10B981" iconBg="bg-green-500/10"   trend={0} trendLabel="stable" />
                  <KPICard title="Stickiness"         value={`${kpis.stickiness_pct.toFixed(1)}%`}    subtitle="DAU / MAU × 100"               icon={Zap}           iconColor="#F59E0B" iconBg="bg-amber-500/10"   trend={0} trendLabel="stable" />
                  <KPICard title="Inactifs"           value={kpis.inactive_count.toLocaleString()}     subtitle="No activity for 7+ days"       icon={AlertTriangle} iconColor="#EF4444" iconBg="bg-red-500/10"     trend={0} trendLabel="negative" alert={kpis.inactive_count > 100} />
                  <KPICard title="Durée de vie"       value={`${kpis.avg_lifetime_days.toFixed(0)}j`} subtitle="Average subscription duration" icon={Clock}         iconColor="#8B5CF6" iconBg="bg-violet-500/10"  trend={0} trendLabel="stable" />
                </>
              ) : null
            }
          </div>
        )}

        {/* ── DAU Trend Chart ───────────────────────────────── */}
        {!activityError && (
          <div>
            {activityLoading
              ? <ChartSkeleton />
              : activityData?.dau_trend
                ? <DAUTrendChart data={activityData.dau_trend} />
                : null
            }
          </div>
        )}

        {/* ── Service Activity & User Growth ────────────────── */}
        {!activityError && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {activityLoading
              ? <><ChartSkeleton /><ChartSkeleton /></>
              : (
                <>
                  {activityData?.by_service && (
                    <ServiceActivityTable data={activityData.by_service} />
                  )}
                  <UserGrowthChart data={activityData?.user_growth ?? []} />
                </>
              )
            }
          </div>
        )}

        {/* ── Activity Heatmap ──────────────────────────────── */}
        {!activityError && (
          <div>
            {activityLoading
              ? <ChartSkeleton />
              : activityData?.activity_heatmap
                ? <ActivityHeatmap data={activityData.activity_heatmap} />
                : null
            }
          </div>
        )}

        {/* ── Table Utilisateurs ────────────────────────────── */}
        <div className="space-y-4">

          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-100">User List</h2>
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
              value={statutFilter}
              onChange={(e) => { setStatutFilter(e.target.value); setPage(1) }}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-sm text-slate-100 focus:outline-none focus:border-violet-500"
            >
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="trial">Trial</option>
              <option value="inactive">Inactive</option>
              <option value="churned">Churned</option>
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
              onClick={() => { refetchUsers(); refetchActivity() }}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-700 hover:bg-slate-600 border border-slate-600 text-slate-300 rounded transition"
            >
              <RotateCcw size={14} /> Refresh
            </button>
          </div>

          {/* ── Erreur table ──────────────────────────────────── */}
          {usersError && (
            <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
              <p className="flex-1 text-sm text-red-200">{usersError}</p>
              <button
                onClick={refetchUsers}
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
                      { label: "Number",        field: "phone_number"     },
                      { label: "Status",        field: "status"           },
                      { label: "Services",      field: null               },
                      { label: "Registered on", field: "created_at"       },
                      { label: "Last activity", field: "last_activity_at" },
                      { label: "Campaign",      field: null               },
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
                  {usersLoading
                    ? Array.from({ length: ITEMS_PER_PAGE }).map((_, i) => <RowSkeleton key={i} />)
                    : sortedUsers.length === 0
                      ? (
                        <tr>
                          <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                            <Users size={32} className="mx-auto mb-2 opacity-30" />
                            No users found
                          </td>
                        </tr>
                      )
                      : sortedUsers.map((user) => {
                          const cfg = STATUT_MAP[user.status] ?? STATUT_MAP.inactive
                          return (
                            <tr key={user.id} className="hover:bg-slate-800/30 transition cursor-pointer">
                              <td className="px-6 py-4 font-mono text-slate-200 text-xs">
                                {user.phone_number ?? "—"}
                              </td>
                              <td className="px-6 py-4">
                                <span className={`inline-block px-3 py-1 rounded text-xs font-medium border ${cfg.bg} ${cfg.text} ${cfg.border}`}>
                                  {cfg.label}
                                </span>
                              </td>
                              <td className="px-6 py-4">
                                <div className="flex flex-wrap gap-1">
                                  {(user.services ?? []).length > 0
                                    ? (user.services ?? []).map((s, idx) => (
                                        <span key={s.id ?? idx} className="px-2 py-0.5 bg-slate-700 text-slate-300 text-xs rounded">
                                          {s.name}
                                        </span>
                                      ))
                                    : <span className="text-slate-500 text-xs">—</span>
                                  }
                                </div>
                              </td>
                              <td className="px-6 py-4 text-slate-400 text-xs">
                                {user.created_at
                                  ? new Date(user.created_at).toLocaleDateString("en-GB")
                                  : "—"}
                              </td>
                              <td className="px-6 py-4 text-slate-400 text-xs">
                                {user.last_activity_at
                                  ? new Date(user.last_activity_at).toLocaleDateString("en-GB")
                                  : "—"}
                              </td>
                              <td className="px-6 py-4 text-xs">
                                {user.campaign_name ? (
                                  <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 text-[10px] max-w-[120px] truncate inline-block">
                                    {user.campaign_name}
                                  </span>
                                ) : (
                                  <span className="text-slate-500">—</span>
                                )}
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
