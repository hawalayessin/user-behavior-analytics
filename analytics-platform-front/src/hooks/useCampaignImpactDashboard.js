import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import { getWithCache } from "../services/api"

/**
 * Hook for Campaign Impact Dashboard
 * Fetches complete dashboard data: KPIs, charts (by_type, monthly_trend, top_campaigns)
 * Uses caching to optimize repeated requests
 * Supports date range filtering
 */
export function useCampaignImpactDashboard(filters = {}) {
  const normalizedFilters = useMemo(() => ({
    start_date: filters?.start_date ?? null,
    end_date: filters?.end_date ?? null,
    service_id: filters?.service_id ?? null,
  }), [filters?.end_date, filters?.service_id, filters?.start_date])

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: [
      "analytics",
      "campaigns",
      "dashboard",
      normalizedFilters.start_date,
      normalizedFilters.end_date,
      normalizedFilters.service_id,
    ],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (normalizedFilters.start_date) params.set("start_date", normalizedFilters.start_date)
      if (normalizedFilters.end_date) params.set("end_date", normalizedFilters.end_date)
      if (normalizedFilters.service_id) params.set("service_id", normalizedFilters.service_id)

      const qs = params.toString()
      const url = `/analytics/campaigns/dashboard${qs ? `?${qs}` : ""}`
      return await getWithCache(url, { ttlMs: 30000 })
    },
  })

  return {
    data,
    isLoading,
    error: error?.response?.data?.detail ?? error?.message ?? null,
    refetch,
  }
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
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: [
      "analytics",
      "campaigns",
      "list",
      status,
      campaign_type,
      start_date,
      end_date,
      service_id,
      page,
      limit,
    ],
    queryFn: async () => {
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
      return await getWithCache(url, { ttlMs: 10000 })
    },
  })

  return {
    data,
    isLoading,
    error: error?.response?.data?.detail ?? error?.message ?? null,
    refetch,
  }
}
