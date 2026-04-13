import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  Download,
  RotateCcw,
  TrendingUp,
  Target,
  Award,
} from "lucide-react";

import AppLayout from "../../components/layout/AppLayout";
import FilterBar from "../../components/dashboard/FilterBar";

// Use new dashboard hook instead of multiple hooks
import {
  useCampaignImpactDashboard,
  useCampaignList,
} from "../../hooks/useCampaignImpactDashboard";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";
import CampaignPerformanceChart from "../../components/dashboard/campaign/CampaignPerformanceChart";

function SkeletonCard() {
  return (
    <div className="w-full h-28 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
  );
}

function SkeletonBlock({ h = "h-80" }) {
  return (
    <div
      className={`w-full ${h} bg-slate-800 animate-pulse rounded-xl border border-slate-700`}
    />
  );
}

export default function CampaignImpactPage() {
  const [filters, setFilters] = useState(DEFAULT_ANALYTICS_FILTERS);
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState(null);
  const [toast, setToast] = useState(null);

  // Use new dashboard hook with filters (single endpoint, cached)
  const {
    data: dashboard,
    isLoading: dashLoading,
    error: dashError,
    refetch: refetchDashboard,
  } = useCampaignImpactDashboard(filters);

  // Use campaign list for table (paginated, filtered)
  const {
    data: listData,
    isLoading: listLoading,
    error: listError,
    refetch: refetchList,
  } = useCampaignList({
    status: null,
    campaign_type: null,
    start_date: filters?.start_date ?? null,
    end_date: filters?.end_date ?? null,
    service_id: filters?.service_id ?? null,
    page,
    limit: 10,
  });

  // Extract data from dashboard
  const kpis = dashboard?.kpis ?? {};
  const dataQuality = dashboard?.data_quality ?? {};
  const byTypeData = dashboard?.charts?.by_type ?? [];
  const monthlyTrendRaw = dashboard?.charts?.monthly_trend ?? [];
  const topCampaigns = dashboard?.charts?.top_campaigns ?? [];

  const smsSentKpi = useMemo(() => {
    const raw = kpis.total_messages_sent;
    if (raw !== null && raw !== undefined) return Number(raw) || 0;
    return Number(kpis.total_targeted ?? 0) || 0;
  }, [kpis.total_messages_sent, kpis.total_targeted]);

  const effectiveDataQuality = useMemo(() => {
    const hasBackendQuality =
      dataQuality &&
      dataQuality.quality_status !== undefined &&
      dataQuality.quality_score !== undefined;

    if (hasBackendQuality) {
      return {
        quality_score: Number(dataQuality.quality_score ?? 0),
        quality_status: dataQuality.quality_status ?? "poor",
        target_coverage_pct: Number(dataQuality.target_coverage_pct ?? 0),
        sms_coverage_pct: Number(dataQuality.sms_coverage_pct ?? 0),
        delivery_success_pct: Number(dataQuality.delivery_success_pct ?? 0),
      };
    }

    const totalTargeted = Number(kpis.total_targeted ?? 0);
    const qualifiedTargeted = Number(kpis.qualified_targeted ?? 0);
    const totalMessagesSent = Number(kpis.total_messages_sent ?? totalTargeted);
    const totalMessagesDelivered = Number(kpis.total_messages_delivered ?? 0);

    const targetCoverage =
      totalTargeted > 0 ? (qualifiedTargeted / totalTargeted) * 100 : 0;
    const smsCoverage =
      totalTargeted > 0 ? (totalMessagesSent / totalTargeted) * 100 : 0;
    const deliverySuccess =
      totalMessagesSent > 0
        ? (totalMessagesDelivered / totalMessagesSent) * 100
        : 0;

    const qualityScore =
      0.45 * targetCoverage +
      0.25 * Math.min(smsCoverage, 100) +
      0.3 * deliverySuccess;

    let qualityStatus = "poor";
    if (qualityScore >= 85) qualityStatus = "excellent";
    else if (qualityScore >= 70) qualityStatus = "good";
    else if (qualityScore >= 50) qualityStatus = "fair";

    return {
      quality_score: Number(qualityScore.toFixed(1)),
      quality_status: qualityStatus,
      target_coverage_pct: Number(targetCoverage.toFixed(1)),
      sms_coverage_pct: Number(smsCoverage.toFixed(1)),
      delivery_success_pct: Number(deliverySuccess.toFixed(1)),
    };
  }, [
    dataQuality,
    kpis.qualified_targeted,
    kpis.total_messages_delivered,
    kpis.total_messages_sent,
    kpis.total_targeted,
  ]);

  const subsPer1000SmsKpi = useMemo(() => {
    const raw = kpis.subscriptions_per_1000_sms;
    if (raw !== null && raw !== undefined) return Number(raw) || 0;

    const subs = Number(kpis.total_subscriptions ?? 0) || 0;
    const sent = Number(smsSentKpi ?? 0) || 0;
    if (sent <= 0) return 0;
    return (subs / sent) * 1000;
  }, [kpis.subscriptions_per_1000_sms, kpis.total_subscriptions, smsSentKpi]);

  // Aggregate monthly trend by month (sum across campaign types)
  const monthlyTrend = useMemo(() => {
    const aggregated = {};
    monthlyTrendRaw.forEach((item) => {
      if (!aggregated[item.month]) {
        aggregated[item.month] = {
          month: item.month,
          campaign_count: 0,
          targeted: 0,
          subscriptions: 0,
          first_charges: 0,
          conversion_rate: 0,
        };
      }
      aggregated[item.month].campaign_count += item.campaign_count || 0;
      aggregated[item.month].targeted += item.targeted || 0;
      aggregated[item.month].subscriptions += item.subscriptions || 0;
      aggregated[item.month].first_charges += item.first_charges || 0;
    });

    // Recalculate conversion rate for aggregated data
    const result = Object.values(aggregated).map((agg) => ({
      ...agg,
      conversion_rate:
        agg.targeted > 0 ? (agg.subscriptions / agg.targeted) * 100 : 0,
    }));

    return result;
  }, [monthlyTrendRaw]);

  const trendStats = useMemo(() => {
    const sorted = [...monthlyTrend]
      .filter((m) => m?.month)
      .sort((a, b) => new Date(b.month) - new Date(a.month));

    const latest = sorted[0] ?? null;
    const prev = sorted[1] ?? null;

    const latestSubs = Number(latest?.subscriptions ?? 0);
    const prevSubs = Number(prev?.subscriptions ?? 0);
    const subsGrowthPct =
      prevSubs > 0 ? ((latestSubs - prevSubs) / prevSubs) * 100 : 0;

    const latestConv = Number(latest?.conversion_rate ?? 0);
    const prevConv = Number(prev?.conversion_rate ?? 0);
    const convDeltaPct = latestConv - prevConv;

    const avgConv = Number(kpis.conversion_rate ?? 0);
    const bestConv = Number(topCampaigns[0]?.conversion_rate ?? 0);
    const gapToBestPct = bestConv - avgConv;

    return {
      subsGrowthPct,
      convDeltaPct,
      gapToBestPct,
    };
  }, [kpis.conversion_rate, monthlyTrend, topCampaigns]);

  const qualityAlerts = useMemo(() => {
    const qualityScore = Number(effectiveDataQuality.quality_score ?? 0);
    const targetCoverage = Number(
      effectiveDataQuality.target_coverage_pct ?? 0,
    );
    const smsCoverage = Number(effectiveDataQuality.sms_coverage_pct ?? 0);
    const deliverySuccess = Number(
      effectiveDataQuality.delivery_success_pct ?? 0,
    );

    const alerts = [];

    if (qualityScore < 70) {
      alerts.push({
        level: "critical",
        text: `Global data quality is low (${qualityScore.toFixed(1)}%). KPI interpretation may be biased for this filter scope.`,
      });
    }

    if (targetCoverage < 75) {
      alerts.push({
        level: "warning",
        text: `Target coverage is ${targetCoverage.toFixed(1)}% (< 75%). Review audience extraction and targeting rules.`,
      });
    }

    if (smsCoverage < 85) {
      alerts.push({
        level: "warning",
        text: `SMS coverage is ${smsCoverage.toFixed(1)}% (< 85%). Campaign sends may be incomplete vs targeted base.`,
      });
    }

    if (deliverySuccess < 90) {
      alerts.push({
        level: "warning",
        text: `Delivery success is ${deliverySuccess.toFixed(1)}% (< 90%). Validate operator routing and delivery retries.`,
      });
    }

    return alerts;
  }, [
    effectiveDataQuality.delivery_success_pct,
    effectiveDataQuality.quality_score,
    effectiveDataQuality.sms_coverage_pct,
    effectiveDataQuality.target_coverage_pct,
  ]);

  // Extract data from list
  const campaignRows = listData?.campaigns ?? [];
  const pageInfo = listData
    ? { total: listData.total, pages: listData.pages, page: listData.page }
    : { total: 0, pages: 0, page: 1 };

  // Prepare conversion by service data
  const conversionByService = useMemo(() => {
    if (!campaignRows.length) return [];
    const serviceMap = {};
    campaignRows.forEach((campaign) => {
      const service = campaign.service_name || "Unknown";
      if (!serviceMap[service]) {
        serviceMap[service] = {
          service: service,
          totalTarget: 0,
          totalSubs: 0,
          revenue: 0,
        };
      }
      serviceMap[service].totalTarget += campaign.target_size || 0;
      serviceMap[service].totalSubs += campaign.subscriptions_acquired || 0;
      serviceMap[service].revenue += parseFloat(campaign.total_revenue || 0);
    });

    return Object.values(serviceMap)
      .map((s) => ({
        ...s,
        convRate: s.totalTarget > 0 ? (s.totalSubs / s.totalTarget) * 100 : 0,
      }))
      .sort((a, b) => b.convRate - a.convRate);
  }, [campaignRows]);

  const serviceInsights = useMemo(() => {
    const best = conversionByService[0] ?? null;
    const worst = conversionByService[conversionByService.length - 1] ?? null;
    const avg = Number(kpis.conversion_rate ?? 0);
    return { best, worst, avg };
  }, [conversionByService, kpis.conversion_rate]);

  const rowsWithHealth = useMemo(() => {
    return campaignRows.map((r) => {
      const conv = Number(r.conversion_rate ?? 0);
      let health = {
        label: "critical",
        cls: "bg-red-500/20 text-red-400 border-red-500/30",
      };
      if (conv >= 15)
        health = {
          label: "good",
          cls: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        };
      else if (conv >= 8)
        health = {
          label: "warning",
          cls: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        };
      return { ...r, health: health.label, _healthCls: health.cls };
    });
  }, [campaignRows]);

  const selectedCampaign = useMemo(() => {
    const byId = rowsWithHealth.find((r) => r.id === selectedId);
    if (byId) return byId;
    const topBySubs = rowsWithHealth
      .slice()
      .sort(
        (a, b) =>
          (b.subscriptions_acquired ?? 0) - (a.subscriptions_acquired ?? 0),
      )[0];
    return topBySubs ?? null;
  }, [rowsWithHealth, selectedId]);

  // Default selection = top campaign (when data arrives)
  useEffect(() => {
    if (!selectedId && rowsWithHealth.length) {
      const top = rowsWithHealth
        .slice()
        .sort(
          (a, b) =>
            (b.subscriptions_acquired ?? 0) - (a.subscriptions_acquired ?? 0),
        )[0];
      if (top?.id) setSelectedId(top.id);
    }
  }, [rowsWithHealth, selectedId]);

  const anyError = dashError || listError;
  const anyLoading = dashLoading || listLoading;

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  };

  const exportCSV = () => {
    const headers = [
      "Campaign Name",
      "Type",
      "Status",
      "Send Date",
      "Target",
      "Subs",
      "Conv%",
      "1st Charge%",
      "Health",
    ];
    const body = rowsWithHealth.map((r) => [
      r.name ?? "—",
      r.campaign_type ?? "—",
      r.status ?? "—",
      r.send_datetime
        ? new Date(r.send_datetime).toLocaleDateString("en-GB")
        : "—",
      String(r.target_size ?? 0),
      String(r.subscriptions_acquired ?? 0),
      String(Number(r.conversion_rate ?? 0).toFixed(2)),
      String(Number(r.first_charge_rate ?? 0).toFixed(2)),
      r.health ?? "—",
    ]);
    const escape = (v) => `"${String(v).replace(/"/g, '""')}"`;
    const csv = [headers, ...body]
      .map((row) => row.map(escape).join(","))
      .join("\n");

    if (!csv || !rowsWithHealth.length) return showToast("No data to export");

    const blob = new Blob(["\uFEFF" + csv], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `campaign_impact_${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`${rowsWithHealth.length} rows exported`);
  };

  const retryAll = () => {
    refetchDashboard();
    refetchList();
  };

  return (
    <AppLayout pageTitle="Campaign Impact Analysis">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Campaign Impact Analysis
          </h1>
          <p className="text-sm text-slate-400">
            Track campaign performance and subscription conversions
          </p>
        </div>

        <FilterBar
          onApply={(f) => setFilters(f)}
          defaultPeriod="all"
          appliedFilters={filters}
        />

        {anyError && (
          <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0" />
            <p className="flex-1 text-sm text-red-200">{anyError}</p>
            <button
              onClick={retryAll}
              className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition"
            >
              <RotateCcw size={14} /> Retry
            </button>
          </div>
        )}

        {/* KPI row */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-4">
          {dashLoading ? (
            Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)
          ) : (
            <>
              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/15 flex items-center justify-center">
                    <RotateCcw size={20} className="text-emerald-400" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-1">
                    Total Campaigns
                  </h3>
                  <p className="text-3xl font-bold text-slate-100">
                    {(kpis.total_campaigns ?? 0).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/15 flex items-center justify-center">
                    <TrendingUp size={20} className="text-emerald-400" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-1">
                    New Subscribers
                  </h3>
                  <div className="flex items-baseline gap-2">
                    <p className="text-3xl font-bold text-slate-100">
                      {(kpis.total_subscriptions ?? 0).toLocaleString()}
                    </p>
                    <span
                      className={`text-sm font-medium ${trendStats.subsGrowthPct >= 0 ? "text-emerald-400" : "text-red-400"}`}
                    >
                      {trendStats.subsGrowthPct >= 0 ? "+" : ""}
                      {trendStats.subsGrowthPct.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-orange-500/15 flex items-center justify-center">
                    <Target size={20} className="text-orange-400" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-1">
                    Avg Conversion
                  </h3>
                  <div className="flex items-baseline gap-2">
                    <p className="text-3xl font-bold text-slate-100">
                      {Number(kpis.conversion_rate ?? 0).toFixed(1)}%
                    </p>
                    <span
                      className={`text-sm font-medium ${trendStats.convDeltaPct >= 0 ? "text-emerald-400" : "text-red-400"}`}
                    >
                      {trendStats.convDeltaPct >= 0 ? "+" : ""}
                      {trendStats.convDeltaPct.toFixed(1)} pts
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/15 flex items-center justify-center">
                    <Award size={20} className="text-purple-400" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-1">
                    Best Campaign:
                  </h3>
                  <p className="text-lg font-bold text-purple-300">
                    {topCampaigns[0]?.name ?? "—"}
                  </p>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/15 flex items-center justify-center">
                    <Download size={20} className="text-cyan-400" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-1">
                    SMS Sent
                  </h3>
                  <p className="text-3xl font-bold text-slate-100">
                    {smsSentKpi.toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/15 flex items-center justify-center">
                    <TrendingUp size={20} className="text-blue-400" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-400 mb-1">
                    Subs / 1000 SMS
                  </h3>
                  <p className="text-3xl font-bold text-slate-100">
                    {Number(subsPer1000SmsKpi).toFixed(1)}
                  </p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Data Quality Standardization */}
        {!dashLoading && (
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
            <div className="flex items-center justify-between gap-4 mb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-100">
                  Campaign Data Quality
                </h3>
                <p className="text-sm text-slate-400">
                  Standardized quality controls for selected period/service
                </p>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold uppercase border ${
                  effectiveDataQuality.quality_status === "excellent"
                    ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                    : effectiveDataQuality.quality_status === "good"
                      ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
                      : effectiveDataQuality.quality_status === "fair"
                        ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                        : "bg-red-500/20 text-red-300 border-red-500/30"
                }`}
              >
                {(effectiveDataQuality.quality_status ?? "poor").toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg border border-slate-700 bg-slate-900/40">
                <p className="text-xs text-slate-400 mb-1">Quality Score</p>
                <p className="text-2xl font-bold text-slate-100">
                  {Number(effectiveDataQuality.quality_score ?? 0).toFixed(1)}%
                </p>
              </div>
              <div className="p-4 rounded-lg border border-slate-700 bg-slate-900/40">
                <p className="text-xs text-slate-400 mb-1">Target Coverage</p>
                <p className="text-2xl font-bold text-slate-100">
                  {Number(
                    effectiveDataQuality.target_coverage_pct ?? 0,
                  ).toFixed(1)}
                  %
                </p>
              </div>
              <div className="p-4 rounded-lg border border-slate-700 bg-slate-900/40">
                <p className="text-xs text-slate-400 mb-1">SMS Coverage</p>
                <p className="text-2xl font-bold text-slate-100">
                  {Number(effectiveDataQuality.sms_coverage_pct ?? 0).toFixed(
                    1,
                  )}
                  %
                </p>
              </div>
              <div className="p-4 rounded-lg border border-slate-700 bg-slate-900/40">
                <p className="text-xs text-slate-400 mb-1">Delivery Success</p>
                <p className="text-2xl font-bold text-slate-100">
                  {Number(
                    effectiveDataQuality.delivery_success_pct ?? 0,
                  ).toFixed(1)}
                  %
                </p>
              </div>
            </div>
          </div>
        )}

        {!dashLoading && qualityAlerts.length > 0 && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-5 space-y-3">
            <div className="flex items-center gap-2">
              <AlertCircle size={18} className="text-amber-300" />
              <h3 className="text-sm font-bold text-amber-200 uppercase tracking-wide">
                Data Quality Alerts
              </h3>
            </div>
            <div className="space-y-2">
              {qualityAlerts.map((alert, idx) => (
                <div
                  key={`${alert.level}-${idx}`}
                  className={`rounded-lg border px-3 py-2 text-sm ${
                    alert.level === "critical"
                      ? "bg-red-500/10 border-red-500/30 text-red-200"
                      : "bg-amber-500/10 border-amber-500/30 text-amber-100"
                  }`}
                >
                  {alert.text}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Campaign Performance Chart */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {dashLoading ? (
            <SkeletonBlock />
          ) : (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
              <h3 className="text-lg font-bold text-slate-100 mb-4">
                Campaign Performance Overview
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">
                    Total Sent:{" "}
                    <span className="font-semibold text-slate-200">
                      {(kpis.total_targeted ?? 0).toLocaleString()}
                    </span>
                  </span>
                  <span className="text-slate-400">
                    Delivered:{" "}
                    <span className="font-semibold text-slate-200">
                      {(kpis.total_messages_delivered ?? 0).toLocaleString()}
                    </span>
                  </span>
                  <span className="text-slate-400">
                    Best:{" "}
                    <span className="font-semibold text-slate-200">
                      {(topCampaigns[0]?.subscriptions ?? 0).toLocaleString()}
                    </span>
                  </span>
                  <span className="text-slate-400">
                    Gap:{" "}
                    <span
                      className={`font-semibold ${trendStats.gapToBestPct >= 0 ? "text-emerald-400" : "text-red-400"}`}
                    >
                      {trendStats.gapToBestPct >= 0 ? "+" : ""}
                      {trendStats.gapToBestPct.toFixed(1)} pts
                    </span>
                  </span>
                </div>
                <div className="h-64 bg-slate-900/30 rounded-lg p-4 flex items-end justify-around gap-2">
                  {monthlyTrend.slice(0, 6).map((item, idx) => (
                    <div
                      key={item.month}
                      className="flex-1 flex flex-col items-center gap-2"
                    >
                      <div className="w-full flex items-end justify-center gap-1 h-40">
                        <div
                          className="bg-slate-500 rounded-t opacity-40 flex-1"
                          style={{
                            height: `${(item.campaign_count / Math.max(...monthlyTrend.map((m) => m.campaign_count || 0))) * 100}%`,
                          }}
                        />
                        <div
                          className="bg-slate-900 rounded-t flex-1"
                          style={{
                            height: `${(item.campaign_count / Math.max(...monthlyTrend.map((m) => m.campaign_count || 0))) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-xs text-slate-400">
                        {item.month}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {dashLoading ? (
            <SkeletonBlock />
          ) : (
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
              <h3 className="text-lg font-bold text-slate-100 mb-4">
                Conversion by Service
              </h3>
              <div className="space-y-4">
                {conversionByService.slice(0, 4).map((service, idx) => (
                  <div key={service.service} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-200">
                        {service.service}
                      </span>
                      <span className="text-sm font-semibold text-slate-100">
                        {service.convRate.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-900/50 rounded-full h-6 overflow-hidden relative">
                      <div
                        className="h-full rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(service.convRate, 100)}%`,
                          background:
                            idx === 0
                              ? "#a855f7"
                              : idx === 1
                                ? "#3b82f6"
                                : idx === 2
                                  ? "#10b981"
                                  : "#06b6d4",
                        }}
                      />
                      <div className="absolute right-2 top-1/2 transform -translate-y-1/2 w-px h-3 bg-slate-600/50" />
                    </div>
                  </div>
                ))}
              </div>

              {/* ROI by Service */}
              <div className="border-t border-slate-700/50 pt-4 mt-4">
                <h4 className="text-sm font-bold text-slate-100 mb-3">
                  ROI by Service
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  {conversionByService.slice(0, 4).map((service) => (
                    <div
                      key={service.service}
                      className="bg-slate-900/40 border border-slate-700/30 rounded-lg p-3"
                    >
                      <p className="text-xs text-slate-400 mb-1 capitalize">
                        {service.service}
                      </p>
                      <p className="text-lg font-bold text-slate-100">
                        ${(service.revenue / 1000).toFixed(1)}k
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Campaign Details Table */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-100">
                Campaign Details
              </h3>
              <p className="text-sm text-slate-400">
                Filterable campaign list with metrics
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-400">
                {pageInfo.total} campaign{pageInfo.total !== 1 ? "s" : ""}
              </span>
              <button
                onClick={exportCSV}
                className="flex items-center gap-2 px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg transition"
              >
                <Download size={14} />
                Export CSV
              </button>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-700/50 bg-slate-900/40">
            <table className="w-full text-sm">
              <thead className="bg-slate-800 border-b border-slate-700">
                <tr>
                  {[
                    "Name",
                    "Type",
                    "Status",
                    "Date",
                    "Target",
                    "Subs",
                    "Conv%",
                    "1st Charge%",
                    "Health",
                  ].map((h) => (
                    <th
                      key={h}
                      className="px-5 py-3 text-left text-slate-300 font-semibold"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {listLoading ? (
                  Array.from({ length: 10 }).map((_, i) => (
                    <tr key={i}>
                      <td colSpan={9} className="px-5 py-4">
                        <div className="h-4 w-2/3 bg-slate-700 animate-pulse rounded" />
                      </td>
                    </tr>
                  ))
                ) : rowsWithHealth.length === 0 ? (
                  <tr>
                    <td
                      colSpan={9}
                      className="px-6 py-10 text-center text-slate-500"
                    >
                      No campaigns found
                    </td>
                  </tr>
                ) : (
                  rowsWithHealth.map((r) => (
                    <tr
                      key={r.id}
                      className={`hover:bg-slate-800/30 transition cursor-pointer ${
                        selectedId === r.id ? "bg-violet-500/10" : ""
                      }`}
                      onClick={() => setSelectedId(r.id)}
                    >
                      <td className="px-5 py-4 text-slate-100 font-medium">
                        <div className="flex items-center gap-2">
                          {topCampaigns[0]?.id === r.id && (
                            <span className="text-yellow-400">★</span>
                          )}
                          {r.name}
                        </div>
                      </td>
                      <td className="px-5 py-4 text-slate-300 text-xs capitalize">
                        {r.campaign_type}
                      </td>
                      <td className="px-5 py-4 text-slate-300 text-xs capitalize">
                        {r.status}
                      </td>
                      <td className="px-5 py-4 text-slate-400 text-xs">
                        {r.send_datetime
                          ? new Date(r.send_datetime).toLocaleDateString(
                              "en-GB",
                            )
                          : "—"}
                      </td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">
                        {(r.target_size ?? 0).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">
                        {(r.subscriptions_acquired ?? 0).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">
                        {Number(r.conversion_rate ?? 0).toFixed(2)}%
                      </td>
                      <td className="px-5 py-4 text-slate-200 text-xs font-mono">
                        {Number(r.first_charge_rate ?? 0).toFixed(2)}%
                      </td>
                      <td className="px-5 py-4">
                        <span
                          className={`inline-block px-3 py-1 rounded text-xs font-medium border capitalize ${r._healthCls}`}
                        >
                          {r.health}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-400">
              Page {pageInfo.page} / {pageInfo.pages}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(1)}
                disabled={pageInfo.page === 1}
                className="px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                «
              </button>
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={pageInfo.page === 1}
                className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                ←
              </button>
              <span className="px-3 py-1 text-sm text-slate-100 bg-slate-700 rounded font-medium">
                {pageInfo.page}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(pageInfo.pages, p + 1))}
                disabled={pageInfo.page === pageInfo.pages}
                className="px-3 py-1 text-sm hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                →
              </button>
              <button
                onClick={() => setPage(pageInfo.pages)}
                disabled={pageInfo.page === pageInfo.pages}
                className="px-2 py-1 text-xs hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed rounded transition text-slate-300"
              >
                »
              </button>
            </div>
          </div>
        </div>

        {/* Insight Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-800/50 border border-emerald-500/30 rounded-xl p-5 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-emerald-500/20 flex items-center justify-center">
                <span className="text-emerald-400 text-sm">✓</span>
              </div>
              <span className="text-xs font-bold text-emerald-400 uppercase">
                SUCCESS
              </span>
            </div>
            <div>
              <h4 className="font-semibold text-slate-100 mb-1">
                {serviceInsights.best?.service ?? "Service"} Outperforms
              </h4>
              <p className="text-sm text-slate-400">
                {serviceInsights.best?.service ?? "Service"} campaigns convert
                at {Number(serviceInsights.best?.convRate ?? 0).toFixed(1)}%.
                Maintain this allocation and replicate winning messaging.
              </p>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-orange-500/30 rounded-xl p-5 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-orange-500/20 flex items-center justify-center">
                <AlertCircle size={14} className="text-orange-400" />
              </div>
              <span className="text-xs font-bold text-orange-400 uppercase">
                WARNING
              </span>
            </div>
            <div>
              <h4 className="font-semibold text-slate-100 mb-1">
                {serviceInsights.worst?.service ?? "Service"} Underperforming
              </h4>
              <p className="text-sm text-slate-400">
                {serviceInsights.worst?.service ?? "Service"} conversion is{" "}
                {Number(serviceInsights.worst?.convRate ?? 0).toFixed(1)}%.
                Review target quality and timing for this service.
              </p>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-cyan-500/30 rounded-xl p-5 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-cyan-500/20 flex items-center justify-center">
                <span className="text-cyan-400 text-sm">ℹ</span>
              </div>
              <span className="text-xs font-bold text-cyan-400 uppercase">
                INFO
              </span>
            </div>
            <div>
              <h4 className="font-semibold text-slate-100 mb-1">
                D7 Retention Drop
              </h4>
              <p className="text-sm text-slate-400">
                Global campaign conversion is{" "}
                {Number(serviceInsights.avg ?? 0).toFixed(1)}%. Prioritize
                reactivation and upsell waves to improve paid conversion.
              </p>
            </div>
          </div>
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2 px-4 py-3 rounded-lg border border-slate-600 bg-slate-800 text-sm text-slate-100 shadow-xl">
          {toast}
        </div>
      )}
    </AppLayout>
  );
}
