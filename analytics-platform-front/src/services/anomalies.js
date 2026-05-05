import api from "./api"

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
    const res = await api.get("/anomalies/summary", { params: withFilterParams(filters) })
    return res.data
}

export async function getAnomalyTimeline(filters) {
    const res = await api.get("/anomalies/timeline", { params: withFilterParams(filters) })
    return res.data
}

export async function getAnomalyDistribution(filters) {
    const res = await api.get("/anomalies/distribution", { params: withFilterParams(filters) })
    return res.data
}

export async function getAnomalyHeatmap(filters) {
    const res = await api.get("/anomalies/heatmap", { params: withFilterParams(filters) })
    return res.data
}

export async function getAnomalyDetails(filters) {
    const params = withFilterParams(filters, {
        limit: filters.limit ?? 10,
        offset: filters.offset ?? 0,
    })
    const res = await api.get("/anomalies/details", { params })
    return res.data
}

export async function getAnomalyInsights(filters) {
    const res = await api.get("/anomalies/insights", { params: withFilterParams(filters) })
    return res.data
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
