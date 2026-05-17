import { useState, useEffect, useCallback } from "react"
import { getWithCache } from "../services/api"

export function useRetentionHeatmap({ service_id, last_n_months = 6 } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchHeatmap = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const payload = await getWithCache("/analytics/retention/heatmap", {
        params: {
          service_id,
          last_n_months: last_n_months ? String(last_n_months) : null,
        },
        ttlMs: 5 * 60 * 1000,
      })
      setData(payload)
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

