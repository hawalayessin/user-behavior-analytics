import { useMemo } from "react"
import { keepPreviousData, useQuery } from "@tanstack/react-query"
import api from "../services/api"

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
    staleTime: 30 * 1000,
    gcTime: 10 * 60 * 1000,
    cacheTime: 10 * 60 * 1000,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
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