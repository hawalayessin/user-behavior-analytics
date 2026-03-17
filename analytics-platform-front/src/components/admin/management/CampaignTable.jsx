import PropTypes from "prop-types"
import { Pencil, Trash2 } from "lucide-react"

function statusBadge(status) {
  if (status === "completed") return "bg-slate-500/20 text-slate-400 border-slate-500/30"
  if (status === "scheduled") return "bg-blue-500/20 text-blue-400 border-blue-500/30"
  return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
}

export default function CampaignTable({ rows, onEdit, onDelete }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-900/40">
      <table className="w-full text-sm">
        <thead className="bg-slate-800 border-b border-slate-700">
          <tr>
            {["Name", "Service", "Date", "Target", "Subs", "Conv%", "Status", "Edit"].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-slate-300 font-semibold">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={8} className="px-6 py-10 text-center text-slate-500">
                No campaigns found
              </td>
            </tr>
          ) : (
            rows.map((r) => (
              <tr key={r.id} className="hover:bg-slate-700/30 transition">
                <td className="px-5 py-4 text-slate-100 font-medium">{r.name}</td>
                <td className="px-5 py-4 text-slate-300 text-xs">{r.service_name ?? "—"}</td>
                <td className="px-5 py-4 text-slate-400 text-xs">{r.send_date ?? "—"}</td>
                <td className="px-5 py-4 text-slate-200 text-xs font-mono">{(r.target_size ?? 0).toLocaleString()}</td>
                <td className="px-5 py-4 text-slate-200 text-xs font-mono">{(r.total_subs ?? 0).toLocaleString()}</td>
                <td className="px-5 py-4 text-slate-200 text-xs font-mono">{Number(r.conversion_rate ?? 0).toFixed(2)}%</td>
                <td className="px-5 py-4">
                  <span className={`inline-block px-3 py-1 rounded text-xs font-medium border capitalize ${statusBadge(r.status)}`}>
                    {r.status}
                  </span>
                </td>
                <td className="px-5 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onEdit(r)}
                      className="p-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 transition"
                      aria-label="Edit campaign"
                    >
                      <Pencil size={15} />
                    </button>
                    <button
                      onClick={() => onDelete(r)}
                      className="p-2 rounded-lg border border-slate-700 text-red-300 hover:bg-red-500/10 transition"
                      aria-label="Delete campaign"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

CampaignTable.propTypes = {
  rows: PropTypes.array.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
}

