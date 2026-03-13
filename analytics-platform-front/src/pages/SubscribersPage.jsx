import { useState, useEffect } from "react"
import { ChevronDown, ChevronUp, Download, Search, AlertCircle } from "lucide-react"
import PropTypes from "prop-types"
import AppLayout from "../components/layout/AppLayout"
import api from "../services/api"
import UserRowDetail from "../components/subscribers/UserRowDetail"

function SubscriberFilters({ filters, onFiltersChange, services, loading }) {
  const [isServiceOpen, setIsServiceOpen] = useState(false)

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3 mb-6">
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="flex-1 min-w-[200px] relative">
          <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Rechercher par email, téléphone..."
            value={filters.search || ""}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-violet-500"
          />
        </div>

        {/* Status Filter */}
        <div className="relative">
          <button
            onClick={() => setIsServiceOpen(false)}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition"
          >
            <span>Status</span>
            <ChevronDown size={14} />
          </button>
        </div>

        {/* Campaign Filter */}
        <div className="relative">
          <button
            onClick={() => setIsServiceOpen(false)}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition"
          >
            <span>Campaign</span>
            <ChevronDown size={14} />
          </button>
        </div>

        {/* Service Filter */}
        <div className="relative">
          <button
            onClick={() => setIsServiceOpen(!isServiceOpen)}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition"
          >
            <span>Service</span>
            <ChevronDown size={14} className={`transition-transform ${isServiceOpen ? "rotate-180" : ""}`} />
          </button>
          {isServiceOpen && (
            <div className="absolute top-full mt-2 min-w-[200px] bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
              <button
                onClick={() => {
                  onFiltersChange({ ...filters, service_id: null })
                  setIsServiceOpen(false)
                }}
                className="block w-full text-left px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 first:rounded-t-lg transition"
              >
                Tous les services
              </button>
              {services.map((service) => (
                <button
                  key={service.id}
                  onClick={() => {
                    onFiltersChange({ ...filters, service_id: service.id })
                    setIsServiceOpen(false)
                  }}
                  className={`block w-full text-left px-4 py-2 text-sm transition ${
                    filters.service_id === service.id
                      ? "bg-violet-700 text-white"
                      : "text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  {service.name}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

SubscriberFilters.propTypes = {
  filters: PropTypes.object.isRequired,
  onFiltersChange: PropTypes.func.isRequired,
  services: PropTypes.array.isRequired,
  loading: PropTypes.bool,
}

export default function SubscribersPage() {
  const [subscribers, setSubscribers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ search: "", service_id: null })
  const [services, setServices] = useState([])
  const [expandedRow, setExpandedRow] = useState(null)

  // Load services
  useEffect(() => {
    api
      .get("/services")
      .then((res) => setServices(res.data ?? []))
      .catch(() => setServices([]))
  }, [])

  // Load subscribers
  useEffect(() => {
    const fetchSubscribers = async () => {
      setLoading(true)
      setError(null)
      try {
        const params = new URLSearchParams()
        if (filters.search) params.append("search", filters.search)
        if (filters.service_id) params.append("service_id", filters.service_id)

        const response = await api.get(`/users?${params.toString()}`)
        setSubscribers(response.data ?? [])
      } catch (err) {
        setError(err?.response?.data?.message || "Erreur lors du chargement des abonnés")
      } finally {
        setLoading(false)
      }
    }

    fetchSubscribers()
  }, [filters])

  const handleExportCSV = () => {
    if (!subscribers || subscribers.length === 0) return

    const headers = [
      "Email",
      "Téléphone",
      "Abonnements",
      "Services",
      "Statut",
      "Churné",
      "Inactif depuis",
      "Dernière activité",
    ]

    const rows = subscribers.map((user) => [
      user.email || "",
      user.phone_number ? `+216 9${user.phone_number.slice(1, 3)} XXX XXX` : "",
      user.subscriptions?.length || 0,
      user.services?.map((s) => s.name).join("; ") || "—",
      user.status || "—",
      user.has_churned ? "Oui" : "Non",
      user.inactive_days ? `${user.inactive_days}j` : "Jamais actif",
      user.last_activity || "—",
    ])

    const csv = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
    ].join("\n")

    const blob = new Blob([csv], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `users_export_${new Date().toISOString().split("T")[0]}.csv`
    link.click()
  }

  const maskPhone = (phone) => {
    if (!phone) return "—"
    return `+216 9${phone.slice(1, 3)} XXX XXX`
  }

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { bg: "bg-emerald-500/20", color: "text-emerald-300", label: "Actif" },
      trial: { bg: "bg-orange-500/20", color: "text-orange-300", label: "Essai" },
      inactive: { bg: "bg-slate-500/20", color: "text-slate-300", label: "Inactif" },
      churned: { bg: "bg-red-500/20", color: "text-red-300", label: "Churné" },
    }
    const config = statusConfig[status] || statusConfig.inactive
    return <span className={`px-2 py-1 rounded text-xs font-medium ${config.bg} ${config.color}`}>{config.label}</span>
  }

  const getInactivityBadge = (inactiveDays) => {
    if (inactiveDays === null || inactiveDays === undefined) {
      return <span className="text-xs text-slate-500 italic">Jamais actif</span>
    }
    if (inactiveDays < 7) {
      return <span className="flex items-center gap-1 text-xs text-emerald-400">✅ Actif</span>
    }
    if (inactiveDays < 30) {
      return <span className="flex items-center gap-1 text-xs text-orange-400">🟠 {inactiveDays}j</span>
    }
    return <span className="flex items-center gap-1 text-xs text-red-400">⚠️ {inactiveDays}j</span>
  }

  const getServiceBadges = (services) => {
    if (!services || services.length === 0) return "—"
    if (services.length === 1) {
      return (
        <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-slate-700 text-slate-300">
          {services[0].name}
        </span>
      )
    }
    return (
      <span className="inline-block px-2 py-1 rounded text-xs font-medium bg-violet-700 text-violet-200">
        {services[0].name} +{services.length - 1}
      </span>
    )
  }

  return (
    <AppLayout pageTitle="Abonnés">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Gestion des abonnés</h1>
            <p className="text-sm text-slate-400">Liste complète des utilisateurs et leurs abonnements</p>
          </div>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-violet-700 hover:bg-violet-800 text-white text-sm font-semibold rounded-lg transition"
          >
            <Download size={16} />
            Exporter CSV
          </button>
        </div>

        {/* Filters */}
        <SubscriberFilters
          filters={filters}
          onFiltersChange={setFilters}
          services={services}
          loading={loading}
        />

        {/* Error State */}
        {error && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-200">{error}</p>
          </div>
        )}

        {/* Table */}
        {!error && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            {loading ? (
              <div className="p-8 text-center">
                <div className="inline-block animate-spin">
                  <div className="w-8 h-8 border-4 border-slate-700 border-t-violet-500 rounded-full" />
                </div>
                <p className="mt-4 text-slate-400">Chargement des abonnés...</p>
              </div>
            ) : subscribers.length === 0 ? (
              <div className="p-8 text-center text-slate-400">Aucun abonné trouvé</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b border-slate-700 bg-slate-800/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-slate-300 font-semibold">Email</th>
                      <th className="px-6 py-3 text-left text-slate-300 font-semibold">Téléphone</th>
                      <th className="px-6 py-3 text-center text-slate-300 font-semibold">Abonnements</th>
                      <th className="px-6 py-3 text-left text-slate-300 font-semibold">Service(s)</th>
                      <th className="px-6 py-3 text-left text-slate-300 font-semibold">Statut</th>
                      <th className="px-6 py-3 text-left text-slate-300 font-semibold">Churné</th>
                      <th className="px-6 py-3 text-left text-slate-300 font-semibold">Inactif depuis</th>
                      <th className="px-6 py-3 text-center text-slate-300 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {subscribers.map((user) => (
                      <tbody key={user.id}>
                        <tr className="hover:bg-slate-800/30 transition cursor-pointer">
                          <td className="px-6 py-4 text-slate-200 font-medium">{user.email}</td>
                          <td className="px-6 py-4 text-slate-400 text-sm">{maskPhone(user.phone_number)}</td>
                          <td className="px-6 py-4 text-center text-slate-300">
                            {user.subscriptions?.length || 0}
                          </td>
                          <td className="px-6 py-4">{getServiceBadges(user.services)}</td>
                          <td className="px-6 py-4">{getStatusBadge(user.status)}</td>
                          <td className="px-6 py-4 text-sm">
                            {user.has_churned ? (
                              <span className="text-red-400">⚠️ Oui</span>
                            ) : (
                              <span className="text-emerald-400">✅ Non</span>
                            )}
                          </td>
                          <td className="px-6 py-4">{getInactivityBadge(user.inactive_days)}</td>
                          <td className="px-6 py-4 text-center">
                            <button
                              onClick={() =>
                                setExpandedRow(expandedRow === user.id ? null : user.id)
                              }
                              className="p-1 hover:bg-slate-700 rounded transition"
                            >
                              {expandedRow === user.id ? (
                                <ChevronUp size={18} className="text-violet-400" />
                              ) : (
                                <ChevronDown size={18} className="text-slate-500" />
                              )}
                            </button>
                          </td>
                        </tr>

                        {/* Expanded Row Detail */}
                        {expandedRow === user.id && (
                          <tr>
                            <td colSpan="8" className="px-0 py-0">
                              <UserRowDetail userId={user.id} onClose={() => setExpandedRow(null)} />
                            </td>
                          </tr>
                        )}
                      </tbody>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
