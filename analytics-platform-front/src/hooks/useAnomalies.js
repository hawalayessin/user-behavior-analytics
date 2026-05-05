import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import {
    getAnomalyDetectionJobStatus,
    getAnomalyDetails,
    getAnomalyDistribution,
    getAnomalyHeatmap,
    getAnomalyInsights,
    getAnomalySummary,
    getAnomalyTimeline,
    startAnomalyDetectionJob,
} from "../services/anomalies"

const EMPTY_ERRORS = {
    summary: null,
    timeline: null,
    distribution: null,
    heatmap: null,
    details: null,
    insights: null,
}

function normalizeError(err) {
    return err?.response?.data?.detail || err?.message || "Unable to load anomaly data"
}

export function useAnomalies({
    filters,
    severity,
    metrics,
    limit = 10,
    offset = 0,
}) {
    const [summary, setSummary] = useState(null)
    const [timeline, setTimeline] = useState({ series: [], anomalies: [] })
    const [distribution, setDistribution] = useState({ severity_distribution: {}, metric_distribution: {} })
    const [heatmap, setHeatmap] = useState({ weeks: [], services: [] })
    const [details, setDetails] = useState({ items: [], total: 0, limit, offset })
    const [insights, setInsights] = useState({ items: [] })

    const [summaryLoading, setSummaryLoading] = useState(false)
    const [timelineLoading, setTimelineLoading] = useState(false)
    const [distributionLoading, setDistributionLoading] = useState(false)
    const [heatmapLoading, setHeatmapLoading] = useState(false)
    const [detailsLoading, setDetailsLoading] = useState(false)
    const [insightsLoading, setInsightsLoading] = useState(false)
    const [runDetectionLoading, setRunDetectionLoading] = useState(false)
    const [detectionJob, setDetectionJob] = useState(null)
    const pollRef = useRef(null)

    const [errors, setErrors] = useState(EMPTY_ERRORS)

    const apiFilters = useMemo(
        () => ({
            startDate: filters?.start_date || null,
            endDate: filters?.end_date || null,
            serviceId: filters?.service_id || null,
            severity,
            metrics,
            limit,
            offset,
        }),
        [filters?.end_date, filters?.service_id, filters?.start_date, limit, metrics, offset, severity]
    )

    const fetchSummary = useCallback(async () => {
        setSummaryLoading(true)
        setErrors((prev) => ({ ...prev, summary: null }))
        try {
            setSummary(await getAnomalySummary(apiFilters))
        } catch (err) {
            setErrors((prev) => ({ ...prev, summary: normalizeError(err) }))
        } finally {
            setSummaryLoading(false)
        }
    }, [apiFilters])

    const fetchTimeline = useCallback(async () => {
        setTimelineLoading(true)
        setErrors((prev) => ({ ...prev, timeline: null }))
        try {
            setTimeline(await getAnomalyTimeline(apiFilters))
        } catch (err) {
            setErrors((prev) => ({ ...prev, timeline: normalizeError(err) }))
        } finally {
            setTimelineLoading(false)
        }
    }, [apiFilters])

    const fetchDistribution = useCallback(async () => {
        setDistributionLoading(true)
        setErrors((prev) => ({ ...prev, distribution: null }))
        try {
            setDistribution(await getAnomalyDistribution(apiFilters))
        } catch (err) {
            setErrors((prev) => ({ ...prev, distribution: normalizeError(err) }))
        } finally {
            setDistributionLoading(false)
        }
    }, [apiFilters])

    const fetchHeatmap = useCallback(async () => {
        setHeatmapLoading(true)
        setErrors((prev) => ({ ...prev, heatmap: null }))
        try {
            setHeatmap(await getAnomalyHeatmap(apiFilters))
        } catch (err) {
            setErrors((prev) => ({ ...prev, heatmap: normalizeError(err) }))
        } finally {
            setHeatmapLoading(false)
        }
    }, [apiFilters])

    const fetchDetails = useCallback(async () => {
        setDetailsLoading(true)
        setErrors((prev) => ({ ...prev, details: null }))
        try {
            setDetails(await getAnomalyDetails(apiFilters))
        } catch (err) {
            setErrors((prev) => ({ ...prev, details: normalizeError(err) }))
        } finally {
            setDetailsLoading(false)
        }
    }, [apiFilters])

    const fetchInsights = useCallback(async () => {
        setInsightsLoading(true)
        setErrors((prev) => ({ ...prev, insights: null }))
        try {
            setInsights(await getAnomalyInsights(apiFilters))
        } catch (err) {
            setErrors((prev) => ({ ...prev, insights: normalizeError(err) }))
        } finally {
            setInsightsLoading(false)
        }
    }, [apiFilters])

    const refetchAll = useCallback(async () => {
        await Promise.all([
            fetchSummary(),
            fetchTimeline(),
            fetchDistribution(),
            fetchHeatmap(),
            fetchDetails(),
            fetchInsights(),
        ])
    }, [fetchDetails, fetchDistribution, fetchHeatmap, fetchInsights, fetchSummary, fetchTimeline])

    const runDetection = useCallback(async () => {
        setRunDetectionLoading(true)
        setDetectionJob(null)
        try {
            const startRes = await startAnomalyDetectionJob({
                startDate: apiFilters.startDate,
                endDate: apiFilters.endDate,
                serviceId: apiFilters.serviceId,
                metrics: apiFilters.metrics,
                severity: apiFilters.severity,
            })
            const jobId = startRes?.job_id
            if (!jobId) throw new Error("Unable to start anomaly detection job")

            return await new Promise((resolve, reject) => {
                pollRef.current = setInterval(async () => {
                    try {
                        const current = await getAnomalyDetectionJobStatus(jobId)
                        setDetectionJob(current)
                        if (!current) return
                        if (current.status === "success") {
                            clearInterval(pollRef.current)
                            pollRef.current = null
                            await refetchAll()
                            resolve(current.result ?? null)
                        } else if (current.status === "failed" || current.status === "not_found") {
                            clearInterval(pollRef.current)
                            pollRef.current = null
                            const msg = current.error || current.message || "Detection failed"
                            reject(new Error(msg))
                        }
                    } catch (pollErr) {
                        clearInterval(pollRef.current)
                        pollRef.current = null
                        reject(pollErr)
                    }
                }, 1500)
            })
        } finally {
            if (pollRef.current) {
                clearInterval(pollRef.current)
                pollRef.current = null
            }
            setRunDetectionLoading(false)
        }
    }, [apiFilters, refetchAll])

    useEffect(() => {
        refetchAll()
    }, [refetchAll])

    return {
        summary,
        timeline,
        distribution,
        heatmap,
        details,
        insights,
        errors,
        summaryLoading,
        timelineLoading,
        distributionLoading,
        heatmapLoading,
        detailsLoading,
        insightsLoading,
        runDetectionLoading,
        detectionJob,
        runDetection,
        refetchAll,
    }
}
