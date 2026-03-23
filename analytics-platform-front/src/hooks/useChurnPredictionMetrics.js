import { useCallback, useEffect, useState } from "react"
import api from "../services/api"

export function useChurnPredictionMetrics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get("/ml/churn/metrics")
      setData(res.data ?? null)
    } catch (err) {
      // 404 => model not trained yet
      setError(err?.response?.data?.detail ?? err.message ?? "Error loading model metrics")
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}

