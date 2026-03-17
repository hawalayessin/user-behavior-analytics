import PropTypes from "prop-types"
import { Pencil, Trash2 } from "lucide-react"

export default function ServiceTable({ rows, onEdit, onDelete }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-900/40">
      <table className="w-full text-sm">
        <thead className="bg-slate-800 border-b border-slate-700">
          <tr>
            {["Name", "Billing", "Price", "Subs", "Campaigns", "Edit"].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-slate-300 font-semibold">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                No services found
              </td>
            </tr>
          ) : (
            rows.map((r) => (
              <tr key={r.id} className="hover:bg-slate-700/30 transition">
                <td className="px-5 py-4 text-slate-100 font-medium">{r.name}</td>
                <td className="px-5 py-4 text-slate-300 text-xs capitalize">{r.billing_type}</td>
                <td className="px-5 py-4 text-slate-200 text-xs font-mono">{Number(r.price ?? 0).toFixed(2)} DT</td>
                <td className="px-5 py-4 text-slate-300 text-xs">
                  <span className="text-slate-200 font-mono">{(r.active_subscriptions ?? 0).toLocaleString()}</span>
                  <span className="text-slate-500"> / {(r.total_subscriptions ?? 0).toLocaleString()}</span>
                </td>
                <td className="px-5 py-4 text-slate-200 text-xs font-mono">{(r.total_campaigns ?? 0).toLocaleString()}</td>
                <td className="px-5 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onEdit(r)}
                      className="p-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 transition"
                      aria-label="Edit service"
                    >
                      <Pencil size={15} />
                    </button>
                    <button
                      onClick={() => onDelete(r)}
                      className="p-2 rounded-lg border border-slate-700 text-red-300 hover:bg-red-500/10 transition"
                      aria-label="Delete service"
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

ServiceTable.propTypes = {
  rows: PropTypes.array.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
}

