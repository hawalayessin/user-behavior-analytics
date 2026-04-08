import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import api from "../services/api"

export function useChurnPredictionScores({ top = 10, threshold = 0.4, store = false, filters = {} } = {}) {
  const normalizedFilters = useMemo(() => ({
    start_date: filters?.start_date ?? null,
    end_date: filters?.end_date ?? null,
    service_id: filters?.service_id ?? null,
  }), [filters?.end_date, filters?.service_id, filters?.start_date])

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: [
      "ml",
      "churn",
      "scores",
      top,
      threshold,
      store,
      normalizedFilters.start_date,
      normalizedFilters.end_date,
      normalizedFilters.service_id,
    ],
    queryFn: async () => {
      const res = await api.get("/ml/churn/scores", {
        params: {
          top,
          threshold,
          store,
          start_date: normalizedFilters.start_date,
          end_date: normalizedFilters.end_date,
          service_id: normalizedFilters.service_id,
        },
      })
      return res.data ?? null
    },
  })

  return {
    data,
    loading: isLoading,
    error: error?.response?.data?.detail ?? error?.message ?? null,
    refetch,
  }
}

