import { useState, useEffect, useCallback } from "react"
import api from "../services/api"

export function useRetentionHeatmap({ service_id, last_n_months = 6 } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchHeatmap = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (service_id) params.set("service_id", service_id)
      if (last_n_months) params.set("last_n_months", String(last_n_months))

      const res = await api.get(`/analytics/retention/heatmap?${params.toString()}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Erreur lors du chargement")
    } finally {
      setLoading(false)
    }
  }, [service_id, last_n_months])

  useEffect(() => {
    fetchHeatmap()
  }, [fetchHeatmap])

  return { data, loading, error, refetch: fetchHeatmap }
}

