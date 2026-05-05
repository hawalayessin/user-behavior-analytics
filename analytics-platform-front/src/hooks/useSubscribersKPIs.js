import { useMemo } from "react"
import { useQuery } from "@tanstack/react-query"
import api from "../services/api"

export function useSubscribersKPIs() {
    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ["subscribers-kpis", "overview-v1"],
        queryFn: async () => {
            const res = await api.get("/analytics/overview")
            return res.data
        },
    })

    const kpis = useMemo(() => {
        const overview = data ?? {}
        return {
            newSubscriptions30d: Number(overview?.subscriptions?.new_last_30_days ?? 0),
            atRiskUsers: Number(overview?.subscriptions?.at_risk_users ?? 0),
            loyaltyScoreAvg: Number(overview?.engagement?.stickiness_pct ?? 0),
            arpuTnd: Number(overview?.revenue?.arpu_current_month ?? 0),
            channelUssd: Number(overview?.users?.channel_counts?.ussd ?? 0),
            channelWeb: Number(overview?.users?.channel_counts?.web ?? 0),
            dataAnchor: overview?.data_anchor ?? null,
        }
    }, [data])

    return {
        kpis,
        loading: isLoading,
        error: error?.response?.data?.detail ?? error?.message ?? null,
        refetch,
    }
}
