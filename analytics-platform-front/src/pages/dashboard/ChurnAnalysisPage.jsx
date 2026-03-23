import { useMemo, useState } from "react"
import { AlertCircle, RotateCcw } from "lucide-react"

import AppLayout from "../../components/layout/AppLayout"
import FilterBar from "../../components/dashboard/FilterBar"
import KPICard from "../../components/dashboard/KPICard"

import { useChurnKPIs } from "../../hooks/useChurnKPIs"
import { useChurnCurve } from "../../hooks/useChurnCurve"
import { useTimeToChurn } from "../../hooks/useTimeToChurn"
import { useChurnReasons } from "../../hooks/useChurnReasons"
import { useRiskSegments } from "../../hooks/useRiskSegments"

import ChurnCurveChart from "../../components/dashboard/churn/ChurnCurveChart"
import TimeToChurnChart from "../../components/dashboard/churn/TimeToChurnChart"
import ChurnReasonsChart from "../../components/dashboard/churn/ChurnReasonsChart"
import RiskSegmentsPanel from "../../components/dashboard/churn/RiskSegmentsPanel"

const KPISkeleton = () => (
  <div className="w-full h-28 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
)
const ChartSkeleton = () => (
  <div className="w-full h-80 bg-slate-800 animate-pulse rounded-xl border border-slate-700" />
)

export default function ChurnAnalysisPage() {
  const [filters, setFilters] = useState({ start_date: null, end_date: null, service_id: null })
  const [churnType, setChurnType] = useState("ALL")

  const kpis = useChurnKPIs(filters)
  const curve = useChurnCurve(filters)
  const ttc = useTimeToChurn({ ...filters, churn_type: churnType })
  const reasons = useChurnReasons({ ...filters, churn_type: churnType })
  const segments = useRiskSegments(filters)

  const anyError = kpis.error || curve.error || ttc.error || reasons.error || segments.error
  const retryAll = () => {
    kpis.refetch()
    curve.refetch()
    ttc.refetch()
    reasons.refetch()
    segments.refetch()
  }

  const kpiCards = useMemo(() => {
    const d = kpis.data
    if (!d) return null
    return {
      global_churn_rate: Number(d.global_churn_rate ?? 0),
      avg_lifetime_days: Number(d.avg_lifetime_days ?? 0),
      first_bill_churn_rate: Number(d.first_bill_churn_rate ?? 0),
      trial_churn_pct: Number(d.trial_churn_pct ?? 0),
      paid_churn_pct: Number(d.paid_churn_pct ?? 0),
      voluntary_pct: Number(d.voluntary_pct ?? 0),
      technical_pct: Number(d.technical_pct ?? 0),
    }
  }, [kpis.data])

  return (
    <AppLayout pageTitle="Churn & Risk Analysis">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Churn & Risk Analysis</h1>
          <p className="text-sm text-slate-400">
            Understand why users leave and which segments are at risk
          </p>
        </div>

        <FilterBar onApply={(f) => setFilters(f)} defaultPeriod="3months" />

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Churn type:</span>
          <select
            value={churnType}
            onChange={(e) => setChurnType(e.target.value)}
            className="px-3 py-2 text-xs bg-[#1A1D27] border border-slate-700 rounded-lg text-slate-200 focus:outline-none"
          >
            <option value="ALL">All</option>
            <option value="VOLUNTARY">Voluntary</option>
            <option value="TECHNICAL">Technical</option>
          </select>
        </div>

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

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {kpis.loading ? (
            Array.from({ length: 5 }).map((_, i) => <KPISkeleton key={i} />)
          ) : (
            kpiCards && (
              <>
                <KPICard
                  title="Global Churn Rate"
                  value={`${kpiCards.global_churn_rate.toFixed(2)}%`}
                  subtitle="Churned / active at start"
                  icon={RotateCcw}
                  iconColor="#F97316"
                  iconBg="bg-orange-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Avg Lifetime (days)"
                  value={kpiCards.avg_lifetime_days.toFixed(1)}
                  subtitle="Among churned users"
                  icon={RotateCcw}
                  iconColor="#6366F1"
                  iconBg="bg-violet-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Trial vs Paid"
                  value={`${kpiCards.trial_churn_pct.toFixed(1)}%`}
                  subtitle={`Paid: ${kpiCards.paid_churn_pct.toFixed(1)}%`}
                  icon={RotateCcw}
                  iconColor="#10B981"
                  iconBg="bg-emerald-500/10"
                  trend={0}
                  trendLabel="mix"
                />
                <KPICard
                  title="First-Bill Churn"
                  value={`${kpiCards.first_bill_churn_rate.toFixed(1)}%`}
                  subtitle="Churn within 7 days after 1st charge"
                  icon={RotateCcw}
                  iconColor="#EF4444"
                  iconBg="bg-red-500/10"
                  trend={0}
                  trendLabel="stable"
                />
                <KPICard
                  title="Voluntary vs Technical"
                  value={`${kpiCards.voluntary_pct.toFixed(1)}%`}
                  subtitle={`Technical: ${kpiCards.technical_pct.toFixed(1)}%`}
                  icon={RotateCcw}
                  iconColor="#F59E0B"
                  iconBg="bg-amber-500/10"
                  trend={0}
                  trendLabel="mix"
                />
              </>
            )
          )}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
          <div className="xl:col-span-3">
            {curve.loading ? <ChartSkeleton /> : <ChurnCurveChart data={curve.data ?? []} />}
          </div>
          <div className="xl:col-span-2">
            {reasons.loading ? (
              <ChartSkeleton />
            ) : (
              <ChurnReasonsChart
                data={reasons.data ?? []}
                churnType={churnType}
                onChangeType={setChurnType}
              />
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
          <div className="xl:col-span-3">
            {ttc.loading ? <ChartSkeleton /> : <TimeToChurnChart data={ttc.data ?? []} />}
          </div>
          <div className="xl:col-span-2">
            {segments.loading ? <ChartSkeleton /> : <RiskSegmentsPanel data={segments.data ?? []} />}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

