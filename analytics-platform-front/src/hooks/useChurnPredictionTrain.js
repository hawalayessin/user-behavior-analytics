import { useCallback, useState } from "react"
import api from "../services/api"

export function useChurnPredictionTrain() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const train = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post("/ml/churn/train")
      return res.data ?? null
    } catch (err) {
      setError(err?.response?.data?.detail ?? err.message ?? "Error training churn model")
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { train, loading, error }
}

