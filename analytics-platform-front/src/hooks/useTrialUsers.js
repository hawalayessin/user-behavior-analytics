import { useState, useEffect, useCallback } from "react"

/**
 * Hook to fetch Trial Users list
 * @param {Object} filters - { status, search, service_id, page, page_size }
 * @returns {Object} { data, loading, error, refetch }
 */
export function useTrialUsers(filters = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (filters?.status)     params.append("status",     String(filters.status))
      if (filters?.search)     params.append("search",     String(filters.search))
      if (filters?.service_id) params.append("service_id", String(filters.service_id))
      if (filters?.page)       params.append("page",       String(filters.page))
      if (filters?.limit)      params.append("page_size",  String(filters.limit))

      const res = await window.fetch(`/api/users/trial?${params.toString()}`)
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const json = await res.json()
      setData(json)
      setError(null)
    } catch (err) {
      console.error("Trial users fetch error:", err)
      setError(err.message || "Failed to fetch trial users")
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [filters?.status, filters?.search, filters?.service_id, filters?.page, filters?.limit])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}
