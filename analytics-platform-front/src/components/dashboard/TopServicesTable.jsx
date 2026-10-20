import { useState } from "react"
import PropTypes from "prop-types"
import { useNavigate } from "react-router-dom"
import {
  AlertTriangle,
  BarChart3,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Download,
  FileText,
  Medal,
} from "lucide-react"
import * as XLSX from "xlsx"

const RANK_COLORS = {
  1: "text-amber-300",
  2: "text-slate-300",
  3: "text-orange-300",
}

function RankCell({ rank }) {
  if (rank <= 3) {
    return (
      <span className="inline-flex h-6 w-6 items-center justify-center">
        <Medal
          size={18}
          className={RANK_COLORS[rank]}
          aria-label={`Rank ${rank}`}
        />
      </span>
    )
  }

  return <span className="text-slate-500">#{rank}</span>
}

function HealthBadge({ pct }) {
  if (pct < 5)  return (
    <span className="px-2 py-0.5 rounded-full text-xs border bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
      Healthy
    </span>
  )
  if (pct <= 10) return (
    <span className="px-2 py-0.5 rounded-full text-xs border bg-amber-500/20 text-amber-400 border-amber-500/30">
      At Risk
    </span>
  )
  return (
    <span className="px-2 py-0.5 rounded-full text-xs border bg-red-500/20 text-red-400 border-red-500/30">
      Critical
    </span>
  )
}

function churnColor(pct) {
  if (pct < 5)  return "text-emerald-400"
  if (pct <= 10) return "text-amber-400"
  return "text-red-400"
}

export default function TopServicesTable({ services }) {
  const navigate = useNavigate()
  const [exportOpen, setExportOpen] = useState(false)
  const [toast, setToast] = useState(null)

  const showToast = (message, type = "success") => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }

  const healthLabel = (pct) => {
    if (pct < 5) return "Healthy"
    if (pct <= 10) return "At Risk"
    return "Critical"
  }

  const buildRows = (list) =>
    list.map((svc, index) => ({
      Rank: index + 1,
      Service: svc.name,
      "Active Subs": svc.active_subs,
      Churned: svc.churned_subs,
      "Churn Rate %": svc.churn_rate_pct,
      Health: healthLabel(svc.churn_rate_pct),
    }))

  const exportCSV = () => {
    const rows = buildRows(services)
    if (!rows.length) return showToast("No data to export", "warning")

    const headers = [
      "Rank",
      "Service",
      "Active Subs",
      "Churned",
      "Churn Rate %",
      "Health",
    ]
    const csvContent = [
      headers,
      ...rows.map((r) =>
        headers.map((h) => `"${String(r[h]).replace(/"/g, '""')}"`),
      ),
    ]
      .map((row) => row.join(","))
      .join("\n")

    const blob = new Blob(["\uFEFF" + csvContent], {
      type: "text/csv;charset=utf-8;",
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `top_services_${new Date().toISOString().split("T")[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast(`${rows.length} services exported to CSV`)
  }

  const exportExcel = () => {
    const rows = buildRows(services)
    if (!rows.length) return showToast("No data to export", "warning")

    const ws = XLSX.utils.json_to_sheet(rows)
    const wb = XLSX.utils.book_new()
    ws["!cols"] = [
      { wch: 6 },
      { wch: 22 },
      { wch: 12 },
      { wch: 10 },
      { wch: 12 },
      { wch: 10 },
    ]
    XLSX.utils.book_append_sheet(wb, ws, "Top Services")
    XLSX.writeFile(
      wb,
      `top_services_${new Date().toISOString().split("T")[0]}.xlsx`,
    )
    showToast(`${rows.length} services exported to Excel`)
  }

  return (
    <>
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4">
          <h3 className="text-sm font-semibold text-slate-100">Top Services Performance</h3>
          <div className="flex items-center gap-3">
            <div className="export-dropdown relative">
              <button
                onClick={() => setExportOpen((prev) => !prev)}
                className="flex items-center gap-2 px-3 py-1.5 text-sm rounded border border-slate-800 bg-slate-950/50 text-slate-300 hover:text-slate-100 transition"
              >
                <Download size={14} />
                Export
                <ChevronDown size={12} className="opacity-60" />
              </button>

              {exportOpen && (
                <div className="absolute right-0 top-9 z-50 w-44 rounded-lg shadow-xl overflow-hidden border border-slate-800 bg-slate-900">
                  <button
                    onClick={() => {
                      exportCSV()
                      setExportOpen(false)
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-left text-slate-200 hover:bg-slate-800/60 transition"
                  >
                    <FileText size={14} />
                    Export CSV
                  </button>
                  <div className="border-t border-slate-800" />
                  <button
                    onClick={() => {
                      exportExcel()
                      setExportOpen(false)
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-left text-slate-200 hover:bg-slate-800/60 transition"
                  >
                    <BarChart3 size={14} />
                    Export Excel
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={() => navigate("/management/services")}
              className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              <span className="inline-flex items-center gap-1">
                View All Services
                <ChevronRight size={14} />
              </span>
            </button>
          </div>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-950/50 border-b border-slate-800">
              {["Rank", "Service Name", "Active Subs", "Churned", "Churn Rate", "Health Score"].map((h) => (
                <th key={h} className="px-5 py-3 text-left text-xs uppercase tracking-widest text-slate-500 font-medium">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {services.map((svc, i) => (
              <tr
                key={svc.name}
                className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
              >
                <td className="px-5 py-3">
                  <RankCell rank={i + 1} />
                </td>
                <td className="px-5 py-3 text-slate-200 font-medium">{svc.name}</td>
                <td className="px-5 py-3 text-slate-300">{svc.active_subs.toLocaleString()}</td>
                <td className="px-5 py-3 text-slate-400">{svc.churned_subs.toLocaleString()}</td>
                <td className={`px-5 py-3 font-semibold ${churnColor(svc.churn_rate_pct)}`}>
                  {svc.churn_rate_pct}%
                </td>
                <td className="px-5 py-3">
                  <HealthBadge pct={svc.churn_rate_pct} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {toast && (
        <div className="fixed top-6 left-1/2 z-[80] flex w-[calc(100vw-2rem)] max-w-md -translate-x-1/2 items-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-100 shadow-xl">
          {toast.type === "warning" ? (
            <AlertTriangle size={16} className="text-amber-300" />
          ) : (
            <CheckCircle size={16} className="text-emerald-300" />
          )}
          {toast.message}
        </div>
      )}
    </>
  )
}

TopServicesTable.propTypes = {
  services: PropTypes.arrayOf(
    PropTypes.shape({
      name:           PropTypes.string.isRequired,
      active_subs:    PropTypes.number.isRequired,
      churned_subs:   PropTypes.number.isRequired,
      churn_rate_pct: PropTypes.number.isRequired,
    })
  ).isRequired,
}

HealthBadge.propTypes = { pct: PropTypes.number.isRequired }
RankCell.propTypes = { rank: PropTypes.number.isRequired }
