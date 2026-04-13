import { useMemo } from "react"
import { keepPreviousData, useQuery } from "@tanstack/react-query"
import api from "../services/api"

const LONG_CACHE_MS = 24 * 60 * 60 * 1000
const USER_ACTIVITY_QUERY_VERSION = "2026-04-10-v2"

export function useUserActivity({ start_date, end_date, service_id } = {}) {
  const normalized = useMemo(
    () => ({
      start_date: start_date ?? null,
      end_date: end_date ?? null,
      service_id: service_id ?? null,
    }),
    [end_date, service_id, start_date],
  )

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: [
      "analytics",
      "user-activity",
      USER_ACTIVITY_QUERY_VERSION,
      normalized.start_date,
      normalized.end_date,
      normalized.service_id,
    ],
    queryFn: async () => {
      const res = await api.get("/analytics/user-activity", {
        params: {
          start_date: normalized.start_date,
          end_date: normalized.end_date,
          service_id: normalized.service_id,
        },
      })
      return res.data ?? null
    },
    staleTime: 60 * 1000,
    gcTime: LONG_CACHE_MS,
    cacheTime: LONG_CACHE_MS,
    refetchOnMount: "always",
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
    keepPreviousData: true,
    placeholderData: keepPreviousData,
  })

  return {
    data,
    loading: isLoading,
    error: error?.response?.data?.detail ?? error?.message ?? null,
    refetch,
  }
}