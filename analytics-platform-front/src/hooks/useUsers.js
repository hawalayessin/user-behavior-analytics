import { useState, useEffect, useCallback } from "react"
import api from "../services/api"

export function useUsers({ status, search, service_id, page = 1, limit = 10 }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  const fetchUsers = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      params.set("page",      String(page))
      params.set("page_size", String(limit))
      if (status     && status !== "Tous") params.set("status",     status)
      if (search)                          params.set("search",     search)
      if (service_id)                      params.set("service_id", service_id)

      const res = await api.get(`/users?${params.toString()}`)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Erreur lors du chargement")
    } finally {
      setLoading(false)
    }
  }, [status, search, service_id, page, limit])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  return { data, loading, error, refetch: fetchUsers }
}