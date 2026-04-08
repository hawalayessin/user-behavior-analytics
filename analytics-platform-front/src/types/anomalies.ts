export type Severity = "critical" | "high" | "medium";
export type Metric = "dau" | "churn_rate" | "revenue" | "renewals";

export interface AnomalyFilters {
  startDate: string | null;
  endDate: string | null;
  serviceId?: string | null;
  severity?: Severity[];
  metrics?: Metric[];
  limit?: number;
  offset?: number;
}

export interface SummaryResponse {
  anomalies_detected: number;
  critical_alerts: number;
  unresolved: number;
  most_affected_service: { name: string; anomaly_count: number };
  last_detection: { run_at: string | null; next_run: string | null };
  trend_vs_previous: number;
}

export interface TimelinePoint {
  date: string;
  value: number;
}

export interface TimelineResponse {
  series: Array<{ metric: Metric; points: TimelinePoint[] }>;
  anomalies: Array<{
    date: string;
    metric: Metric;
    severity: Severity;
    z_score: number;
    observed_value: number;
    expected_value: number;
    service_name: string;
  }>;
}

export interface DistributionResponse {
  severity_distribution: Record<Severity, number>;
  metric_distribution: Record<Metric, number>;
}

export interface HeatmapResponse {
  weeks: string[];
  services: Array<{
    service_name: string;
    cells: Array<{ week: string; severity_score: number; count: number }>;
  }>;
}

export interface DetailsResponse {
  items: Array<{
    id: string;
    severity: Severity;
    detection_date: string;
    service_name: string;
    metric: Metric;
    observed_value: number;
    expected_value: number;
    z_score: number;
    direction: string;
    status: string;
    anomaly_type: string;
  }>;
  total: number;
  limit: number;
  offset: number;
}

export interface InsightsResponse {
  items: Array<{
    type: "warning" | "critical" | "info";
    title: string;
    body: string;
    action_label: string;
  }>;
}
