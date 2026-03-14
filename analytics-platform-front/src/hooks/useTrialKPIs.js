import { useState, useEffect, useCallback } from "react"

/**
 * Hook to fetch Free Trial KPIs
 * @param {Object} filters - Filter object with start_date, end_date, service_id
 * @returns {Object} { data, loading, error, refetch }
 */
export function useTrialKPIs(filters = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (filters?.start_date) params.append("start_date", filters.start_date)
      if (filters?.end_date) params.append("end_date", filters.end_date)
      if (filters?.service_id) params.append("service_id", filters.service_id)

      const res = await window.fetch(`/api/analytics/trial/kpis?${params.toString()}`)
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const json = await res.json()
      setData(json)
      setError(null)
    } catch (err) {
      console.error("KPI fetch error:", err)
      setError(err.message || "Failed to fetch trial KPIs")
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [filters?.start_date, filters?.end_date, filters?.service_id])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}
