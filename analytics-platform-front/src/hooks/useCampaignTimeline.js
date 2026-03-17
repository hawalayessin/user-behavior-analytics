import { useCallback, useEffect, useState } from "react"
import api from "../services/api"

export function useCampaignTimeline({ start_date, end_date, service_id } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchTimeline = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (start_date) params.set("start_date", start_date)
      if (end_date) params.set("end_date", end_date)
      if (service_id) params.set("service_id", service_id)

      const qs = params.toString()
      const res = await api.get(`/analytics/campaigns/timeline${qs ? `?${qs}` : ""}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Erreur lors du chargement")
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [start_date, end_date, service_id])

  useEffect(() => {
    fetchTimeline()
  }, [fetchTimeline])

  return { data, loading, error, refetch: fetchTimeline }
}

