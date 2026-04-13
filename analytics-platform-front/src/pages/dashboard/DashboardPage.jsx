import { useMemo, useState } from "react";
import {
  AlertCircle,
  RefreshCw,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import AppLayout from "../../components/layout/AppLayout";
import FilterBar from "../../components/dashboard/FilterBar";
import TabNavigation from "../../components/dashboard/TabNavigation";
import OverviewTab from "../../components/dashboard/tabs/OverviewTab";
import EngagementTab from "../../components/dashboard/tabs/EngagementTab";
import RevenueTab from "../../components/dashboard/tabs/RevenueTab";
import TrialChurnTab from "../../components/dashboard/tabs/TrialChurnTab";
import { DEFAULT_ANALYTICS_FILTERS } from "../../constants/dateFilters";
import { useOverview } from "../../hooks/useOverview";
import { useNRR } from "../../hooks/useNRR";

const DEFAULT_FILTERS = DEFAULT_ANALYTICS_FILTERS;

// ── Skeleton ───────────────────────────────────────────────────────────────────
function SkeletonBlock({ className }) {
  return (
    <div className={`animate-pulse bg-slate-800 rounded-xl ${className}`} />
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 7 }).map((_, i) => (
          <SkeletonBlock key={i} className="h-32" />
        ))}
      </div>
      <div className="flex gap-4">
        <SkeletonBlock className="h-72 flex-1" />
        <SkeletonBlock className="h-72 flex-1" />
      </div>
      <SkeletonBlock className="h-64" />
      <SkeletonBlock className="h-56" />
    </div>
  );
}

// ── Error ──────────────────────────────────────────────────────────────────────
function DashboardError({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center h-96 gap-4">
      <AlertCircle size={48} className="text-red-400" />
      <p className="text-slate-400 text-sm">{message}</p>
      <button
        onClick={onRetry}
        className="flex items-center gap-2 px-4 py-2 bg-violet-700 hover:bg-violet-800 text-white text-sm font-semibold rounded-lg transition"
      >
        <RefreshCw size={15} />
        Réessayer
      </button>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [activeTab, setActiveTab] = useState(0);
  const [guideEnabled, setGuideEnabled] = useState(true);
  const [guideExpanded, setGuideExpanded] = useState(true);
  const normalizedFilters = useMemo(
    () => ({
      start_date: filters.start_date ?? null,
      end_date: filters.end_date ?? null,
      service_id: filters.service_id ?? null,
    }),
    [filters.end_date, filters.service_id, filters.start_date],
  );

  const { data, loading, error, refetch } = useOverview(normalizedFilters);
  const { data: nrr, loading: nrrLoading, error: nrrError } = useNRR();

  const insightGuide = useMemo(() => {
    if (!data) {
      return {
        title: "Insight Guide",
        summary: "Apply filters to generate narrative insights.",
        steps: [],
      };
    }

    const subs = data.subscriptions ?? {};
    const revenue = data.revenue ?? {};
    const engagement = data.engagement ?? {};
    const churn = data.churn ?? {};

    if (activeTab === 0) {
      const conversion = Number(subs.conversion_rate_pct ?? 0);
      const topService = data.top_services?.[0]?.name ?? "N/A";
      return {
        title: "Overview Storyline",
        summary:
          "Use this view to align business context before drilling into engagement, revenue, and churn.",
        steps: [
          {
            heading: "Current scale",
            metric: `${Number(subs.total ?? 0).toLocaleString()} total subscriptions`,
            interpretation:
              "This is your baseline population for all downstream KPIs.",
            action:
              "Validate scope (date/service) before comparing with previous periods.",
          },
          {
            heading: "Conversion health",
            metric: `${conversion.toFixed(1)}% trial-to-paid conversion`,
            interpretation:
              conversion >= 15
                ? "Conversion is strong and supports growth momentum."
                : "Conversion is below target and may limit net growth.",
            action:
              "Prioritize onboarding and early-trial messaging on low-converting segments.",
          },
          {
            heading: "Service contribution",
            metric: `${topService} currently leads in activity`,
            interpretation:
              "Top service behavior often drives aggregate KPI direction.",
            action:
              "Replicate winning patterns from the top service to underperforming services.",
          },
        ],
      };
    }

    if (activeTab === 1) {
      const score = Number(engagement.engagement_score ?? 0);
      const inactivity = Number(engagement.inactivity_rate_pct ?? 0);
      return {
        title: "Engagement Drill-Down",
        summary:
          "Explain why activity changes and which user groups need immediate retention actions.",
        steps: [
          {
            heading: "Global engagement level",
            metric: `${score.toFixed(1)}/100 engagement score`,
            interpretation:
              score >= 70
                ? "Healthy engagement supports better retention outlook."
                : "Engagement is fragile and churn risk is elevated.",
            action:
              "Launch reactivation campaigns for inactive cohorts in the next 7 days.",
          },
          {
            heading: "Inactivity pressure",
            metric: `${inactivity.toFixed(1)}% users inactive over 7 days`,
            interpretation:
              inactivity > 25
                ? "Inactivity is above acceptable threshold."
                : "Inactivity is under control for now.",
            action:
              "Build a weekly inactive-user watchlist with service-level ownership.",
          },
        ],
      };
    }

    if (activeTab === 2) {
      const failedPct = Number(revenue.failed_pct ?? 0);
      const mrr = Number(revenue.mrr ?? 0);
      return {
        title: "Revenue Drill-Down",
        summary:
          "Link payment performance to revenue outcomes and prioritize recovery actions.",
        steps: [
          {
            heading: "Recurring revenue",
            metric: `${mrr.toLocaleString()} DT MRR`,
            interpretation:
              "MRR reflects the near-term value secured by current subscribers.",
            action:
              "Track MRR delta weekly against churn and payment failure trends.",
          },
          {
            heading: "Payment reliability",
            metric: `${failedPct.toFixed(1)}% billing failures`,
            interpretation:
              failedPct > 30
                ? "Payment friction is a major revenue leakage driver."
                : "Billing reliability is acceptable but still improvable.",
            action:
              "Prioritize failed-payment recovery flows and operator routing diagnostics.",
          },
        ],
      };
    }

    const monthlyChurn = Number(churn.churn_rate_month_pct ?? 0);
    const day3Dropoff = Number(churn.dropoff?.day3 ?? 0);
    return {
      title: "Trial & Churn Drill-Down",
      summary:
        "Focus on first-trial days and churn composition to reduce preventable losses.",
      steps: [
        {
          heading: "Monthly churn pressure",
          metric: `${monthlyChurn.toFixed(1)}% monthly churn`,
          interpretation:
            monthlyChurn > 20
              ? "Churn is materially impacting sustainable growth."
              : "Churn is moderate but still requires monitoring.",
          action:
            "Deploy churn-prevention outreach on high-risk users before renewal date.",
        },
        {
          heading: "Critical trial window",
          metric: `${day3Dropoff.toLocaleString()} users dropped by day 3`,
          interpretation:
            "First 72h remains the most sensitive conversion window.",
          action:
            "Add guided onboarding nudges during day 1-3 to reduce early drop-off.",
        },
      ],
    };
  }, [activeTab, data]);

  const errorMessage =
    error?.response?.data?.detail ??
    error?.message ??
    "Impossible de charger les données.";

  return (
    <AppLayout pageTitle="Analytics Overview" hasNotifications showExportButton>
      <div className="space-y-5 pb-6">
        {/* Filter Bar — toujours visible */}
        <FilterBar
          onApply={setFilters}
          appliedFilters={filters}
          anchorDate={data?.usage_data_anchor ?? data?.data_anchor ?? null}
        />

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Contenu */}
        {loading && <DashboardSkeleton />}

        {!loading && error && (
          <DashboardError message={errorMessage} onRetry={refetch} />
        )}

        {!loading && !error && data && (
          <>
            {activeTab === 0 && <OverviewTab data={data} filters={filters} />}
            {activeTab === 1 && <EngagementTab data={data} filters={filters} />}
            {activeTab === 2 && (
              <RevenueTab
                data={data}
                filters={filters}
                nrr={nrr}
                nrrLoading={nrrLoading}
                nrrError={nrrError}
              />
            )}
            {activeTab === 3 && <TrialChurnTab data={data} filters={filters} />}
          </>
        )}

        {/* Insight Guide (narrative drill-down mode) */}
        {!loading && !error && data && (
          <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div className="flex items-center gap-2">
                <BookOpen size={18} className="text-cyan-300" />
                <div>
                  <p className="text-sm font-semibold text-slate-100">
                    Insight Guide
                  </p>
                  <p className="text-xs text-slate-400">
                    Narrative drill-down for non-technical managers
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setGuideEnabled((v) => !v)}
                  className={`px-3 py-1.5 text-xs rounded-lg border transition ${
                    guideEnabled
                      ? "bg-cyan-500/15 text-cyan-200 border-cyan-500/40"
                      : "bg-slate-800 text-slate-300 border-slate-600"
                  }`}
                >
                  {guideEnabled ? "Guide ON" : "Guide OFF"}
                </button>
                {guideEnabled && (
                  <button
                    onClick={() => setGuideExpanded((v) => !v)}
                    className="px-2 py-1.5 text-xs rounded-lg border bg-slate-800 text-slate-300 border-slate-600"
                    aria-label="Toggle guide details"
                  >
                    {guideExpanded ? (
                      <ChevronUp size={14} />
                    ) : (
                      <ChevronDown size={14} />
                    )}
                  </button>
                )}
              </div>
            </div>

            {guideEnabled && guideExpanded && (
              <div className="space-y-3">
                <div className="rounded-lg border border-slate-700 bg-slate-800/40 p-3">
                  <p className="text-sm font-semibold text-slate-100">
                    {insightGuide.title}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    {insightGuide.summary}
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
                  {insightGuide.steps.map((step) => (
                    <div
                      key={step.heading}
                      className="rounded-lg border border-slate-700 bg-slate-800/30 p-3 space-y-2"
                    >
                      <p className="text-xs uppercase tracking-wide text-cyan-300 font-semibold">
                        {step.heading}
                      </p>
                      <p className="text-sm font-bold text-slate-100">
                        {step.metric}
                      </p>
                      <p className="text-xs text-slate-300">
                        {step.interpretation}
                      </p>
                      <p className="text-xs text-emerald-300">
                        Action: {step.action}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
