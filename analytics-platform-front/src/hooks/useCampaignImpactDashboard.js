import { useCallback, useEffect, useState } from "react"
import { getWithCache } from "../services/api"

/**
 * Hook for Campaign Impact Dashboard
 * Fetches complete dashboard data: KPIs, charts (by_type, monthly_trend, top_campaigns)
 * Uses caching to optimize repeated requests
 * Supports date range filtering
 */
export function useCampaignImpactDashboard(filters = {}) {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchDashboard = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      // Build query string from filters
      const params = new URLSearchParams()
      if (filters?.start_date) params.set("start_date", filters.start_date)
      if (filters?.end_date) params.set("end_date", filters.end_date)
      if (filters?.service_id) params.set("service_id", filters.service_id)
      
      const qs = params.toString()
      const url = `/analytics/campaigns/dashboard${qs ? `?${qs}` : ""}`
      
      // Use getWithCache with proper options parameter (object with ttlMs)
      const result = await getWithCache(url, { ttlMs: 30000 })
      setData(result)
    } catch (err) {
      const errorMsg = err.response?.data?.detail ?? err.message ?? "Erreur lors du chargement du dashboard"
      setError(errorMsg)
      setData(null)
    } finally {
      setIsLoading(false)
    }
  }, [filters])  // Use entire filters object as dependency

  useEffect(() => {
    fetchDashboard()
  }, [fetchDashboard])

  return { data, isLoading, error, refetch: fetchDashboard }
}

/**
 * Hook for paginated campaign list with filtering
 */
export function useCampaignList({
  status = null,
  campaign_type = null,
  start_date = null,
  end_date = null,
  service_id = null,
  page = 1,
  limit = 10,
} = {}) {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchList = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (status && status !== "all") params.set("status", status)
      if (campaign_type && campaign_type !== "all") params.set("campaign_type", campaign_type)
      if (start_date) params.set("start_date", start_date)
      if (end_date) params.set("end_date", end_date)
      if (service_id) params.set("service_id", service_id)
      params.set("page", page)
      params.set("limit", limit)

      const qs = params.toString()
      const url = `/analytics/campaigns/list${qs ? `?${qs}` : ""}`
      
      // Use getWithCache with proper options parameter (object with ttlMs)
      const res = await getWithCache(url, { ttlMs: 10000 })  // 10s cache
      setData(res)
    } catch (err) {
      const errorMsg = err.response?.data?.detail ?? err.message ?? "Erreur lors du chargement de la liste"
      setError(errorMsg)
      setData(null)
    } finally {
      setIsLoading(false)
    }
  }, [status, campaign_type, start_date, end_date, service_id, page, limit])

  useEffect(() => {
    fetchList()
  }, [fetchList])

  return { data, isLoading, error, refetch: fetchList }
}
