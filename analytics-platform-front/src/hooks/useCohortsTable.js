import { useState, useEffect, useCallback } from "react"
import api from "../services/api"

export function useCohortsTable({ service_id, page = 1, page_size = 10 } = {}) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  const fetchCohorts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (service_id) params.set("service_id", service_id)
      params.set("page",      String(page))
      params.set("page_size", String(page_size))

      const res = await api.get(`/analytics/retention/cohorts-list?${params.toString()}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Erreur lors du chargement")
    } finally {
      setLoading(false)
    }
  }, [service_id, page, page_size])

  useEffect(() => {
    fetchCohorts()
  }, [fetchCohorts])

  return { data, loading, error, refetch: fetchCohorts }
}

