import { useState, useEffect } from "react"
import PropTypes from "prop-types"
import { X, AlertCircle } from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import api from "../../services/api"

function CustomSparklineTooltip({ active, payload, label }) {
  if (!active || !payload) return null
  return (
    <div className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200">
      {label}: {payload[0]?.value}
    </div>
  )
}

export default function UserRowDetail({ userId, onClose }) {
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await api.get(`/users/${userId}/detail`)
        setDetail(response.data)
      } catch (err) {
        setError(err?.response?.data?.message || "Erreur lors du chargement des détails")
      } finally {
        setLoading(false)
      }
    }

    if (userId) {
      fetchDetail()
    }
  }, [userId])

  return (
    <div className="bg-slate-800/50 border-t border-slate-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h4 className="text-lg font-semibold text-slate-100">Détails utilisateur</h4>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-700 rounded transition text-slate-400 hover:text-slate-200"
        >
          <X size={20} />
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg mb-4">
          <AlertCircle size={18} className="text-red-400" />
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="inline-block animate-spin">
            <div className="w-6 h-6 border-3 border-slate-600 border-t-violet-500 rounded-full" />
          </div>
        </div>
      ) : detail ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Subscriptions */}
          <div className="space-y-3">
            <h5 className="text-sm font-semibold text-slate-200 uppercase">Abonnements</h5>
            {detail.subscriptions && detail.subscriptions.length > 0 ? (
              <div className="space-y-2">
                {detail.subscriptions.map((sub, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-900/50 border border-slate-700 rounded-lg p-3 text-xs space-y-1"
                  >
                    <p className="font-semibold text-slate-100">{sub.service_name}</p>
                    <p className="text-slate-400">
                      <span className="font-medium">Status:</span> {sub.status}
                    </p>
                    <p className="text-slate-400">
                      <span className="font-medium">Depuis:</span> {sub.since_days}j
                    </p>
                    <p className="text-emerald-400 font-medium">
                      Payé: {(sub.total_paid || 0).toFixed(2)} DT
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-xs">Aucun abonnement</p>
            )}
          </div>

          {/* Billing Events */}
          <div className="space-y-3">
            <h5 className="text-sm font-semibold text-slate-200 uppercase">Historique Billing</h5>
            {detail.billing_events && detail.billing_events.length > 0 ? (
              <div className="space-y-1 max-h-96 overflow-y-auto">
                {detail.billing_events.slice(0, 10).map((event, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs py-1">
                    <span className={event.success ? "text-emerald-400" : "text-red-400"}>
                      {event.success ? "✅" : "❌"}
                    </span>
                    <span className="text-slate-400 flex-1">
                      {new Date(event.date).toLocaleDateString("fr-FR")}
                    </span>
                    <span className="text-slate-300 font-medium">
                      {event.amount?.toFixed(2)} DT
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-xs">Aucune transaction</p>
            )}
          </div>

          {/* Activity */}
          <div className="space-y-3">
            <h5 className="text-sm font-semibold text-slate-200 uppercase">Activité</h5>
            {detail.activity_sparkline && detail.activity_sparkline.length > 0 ? (
              <div className="space-y-3">
                {/* Sparkline */}
                <div className="h-20">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={detail.activity_sparkline}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#404854" />
                      <XAxis
                        dataKey="date"
                        tick={false}
                        height={0}
                      />
                      <YAxis hide />
                      <Tooltip content={<CustomSparklineTooltip />} />
                      <Line
                        type="monotone"
                        dataKey="count"
                        stroke="#7C3AED"
                        dot={false}
                        isAnimationActive={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Stats */}
                <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-3 space-y-1 text-xs">
                  <p className="text-slate-400">
                    <span className="font-medium">Ce mois:</span>
                    <span className="text-slate-200 ml-1">
                      {detail.activity_this_month || 0} actions
                    </span>
                  </p>
                  <p className="text-slate-400">
                    <span className="font-medium">Dernière action:</span>
                    <span className="text-slate-200 ml-1">
                      {detail.last_action
                        ? new Date(detail.last_action).toLocaleDateString("fr-FR")
                        : "N/A"}
                    </span>
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-slate-500 text-xs">Aucune activité</p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  )
}

UserRowDetail.propTypes = {
  userId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onClose: PropTypes.func.isRequired,
}
