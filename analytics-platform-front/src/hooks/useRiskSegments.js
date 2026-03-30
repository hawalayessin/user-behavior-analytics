import { useCallback, useEffect, useState } from "react"
import { getWithCache } from "../services/api"

export function useRiskSegments({ start_date, end_date, service_id } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async ({ force = false } = {}) => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (start_date) params.set("start_date", start_date)
      if (end_date) params.set("end_date", end_date)
      if (service_id) params.set("service_id", service_id)
      const qs = params.toString()
      const payload = await getWithCache(`/analytics/churn/risk-segments${qs ? `?${qs}` : ""}`, { force })
      setData(payload)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Error loading data")
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [start_date, end_date, service_id])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: () => fetchData({ force: true }) }
}

