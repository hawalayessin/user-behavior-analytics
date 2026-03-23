import { useCallback, useEffect, useState } from "react"
import api from "../services/api"

export function useChurnPredictionScores({ top = 10, threshold = 0.4, store = false } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get("/ml/churn/scores", {
        params: { top, threshold, store },
      })
      setData(res.data ?? null)
    } catch (err) {
      setError(err?.response?.data?.detail ?? err.message ?? "Error loading churn scores")
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [top, threshold, store])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}

