import api, { getWithCache } from "./api"

function withFilterParams(filters = {}, params = {}) {
    const out = { ...params }
    if (filters.startDate) out.start_date = filters.startDate
    if (filters.endDate) out.end_date = filters.endDate
    if (filters.serviceId) out.service_id = filters.serviceId
    if (filters.severity?.length) out.severity = filters.severity.join(",")
    if (filters.metrics?.length) out.metrics = filters.metrics.join(",")
    return out
}

export async function getAnomalySummary(filters) {
    return await getWithCache("/anomalies/summary", {
        params: withFilterParams(filters),
        ttlMs: 5 * 60 * 1000,
    })
}

export async function getAnomalyTimeline(filters) {
    return await getWithCache("/anomalies/timeline", {
        params: withFilterParams(filters),
        ttlMs: 5 * 60 * 1000,
    })
}

export async function getAnomalyDistribution(filters) {
    return await getWithCache("/anomalies/distribution", {
        params: withFilterParams(filters),
        ttlMs: 5 * 60 * 1000,
    })
}

export async function getAnomalyHeatmap(filters) {
    return await getWithCache("/anomalies/heatmap", {
        params: withFilterParams(filters),
        ttlMs: 5 * 60 * 1000,
    })
}

export async function getAnomalyDetails(filters) {
    const params = withFilterParams(filters, {
        limit: filters.limit ?? 10,
        offset: filters.offset ?? 0,
    })
    return await getWithCache("/anomalies/details", {
        params,
        ttlMs: 2 * 60 * 1000,
    })
}

export async function getAnomalyInsights(filters) {
    return await getWithCache("/anomalies/insights", {
        params: withFilterParams(filters),
        ttlMs: 5 * 60 * 1000,
    })
}

export async function runAnomalyDetection(payload) {
    const body = {
        start_date: payload.startDate,
        end_date: payload.endDate,
        service_id: payload.serviceId ?? null,
        metrics: payload.metrics ?? [],
        severity: payload.severity ?? [],
    }
    const res = await api.post("/anomalies/run-detection", body)
    return res.data
}

export async function startAnomalyDetectionJob(payload) {
    const body = {
        start_date: payload.startDate,
        end_date: payload.endDate,
        service_id: payload.serviceId ?? null,
        metrics: payload.metrics ?? [],
        severity: payload.severity ?? [],
    }
    const res = await api.post("/anomalies/run-detection/start", body)
    return res.data
}

export async function getAnomalyDetectionJobStatus(jobId) {
    const res = await api.get(`/anomalies/run-detection/${jobId}/status`)
    return res.data
}
