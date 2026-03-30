import { useCallback, useEffect, useState } from "react"
import api from "../services/api"

/**
 * useCrossService
 * Fetches all 4 cross-service endpoints in parallel.
 * Accepts optional filters: { start_date, end_date, service_id }
 * Returns { overview, coSubscriptions, migrations, distribution, loading, error, refetch }
 */
export function useCrossService({ start_date, end_date, service_id } = {}) {
    const [overview, setOverview] = useState(null)
    const [coSubscriptions, setCoSubscriptions] = useState(null)
    const [migrations, setMigrations] = useState(null)
    const [distribution, setDistribution] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const fetchAll = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const params = new URLSearchParams()
            if (start_date) params.set("start_date", start_date)
            if (end_date) params.set("end_date", end_date)
            if (service_id) params.set("service_id", service_id)

            const qs = params.toString()
            const suffix = qs ? `?${qs}` : ""

            const [ovRes, coRes, migRes, distRes] = await Promise.all([
                api.get(`/analytics/cross-service/overview${suffix}`),
                api.get(`/analytics/cross-service/co-subscriptions${suffix}`),
                api.get(`/analytics/cross-service/migrations${suffix}`),
                api.get(`/analytics/cross-service/distribution${suffix}`),
            ])
            setOverview(ovRes.data)
            setCoSubscriptions(coRes.data)
            setMigrations(migRes.data)
            setDistribution(distRes.data)
        } catch (err) {
            setError(err.response?.data?.detail ?? err.message ?? "Erreur lors du chargement")
            setOverview(null)
            setCoSubscriptions(null)
            setMigrations(null)
            setDistribution(null)
        } finally {
            setLoading(false)
        }
    }, [start_date, end_date, service_id])

    useEffect(() => {
        fetchAll()
    }, [fetchAll])

    return { overview, coSubscriptions, migrations, distribution, loading, error, refetch: fetchAll }
}
