import { useCallback, useEffect, useState } from "react"
import api from "../services/api"

export function useChurnReasons({ start_date, end_date, service_id, churn_type = "ALL" } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (start_date) params.set("start_date", start_date)
      if (end_date) params.set("end_date", end_date)
      if (service_id) params.set("service_id", service_id)
      if (churn_type && churn_type !== "ALL") params.set("churn_type", churn_type)
      const qs = params.toString()
      const res = await api.get(`/analytics/churn/reasons${qs ? `?${qs}` : ""}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Error loading data")
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [start_date, end_date, service_id, churn_type])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}

