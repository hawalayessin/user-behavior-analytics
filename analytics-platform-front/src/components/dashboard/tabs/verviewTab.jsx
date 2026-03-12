import PropTypes from "prop-types"
import KPICardsRow1          from "../KPICardsRow1"
import KPICardsRow2          from "../KPICardsRow2"
import SubscriptionDonutChart from "../SubscriptionDonutChart"
import ChurnPieChart         from "../ChurnPieChart"
import TrialDropoffChart     from "../TrialDropoffChart"
import EngagementHealthPanel from "../EngagementHealthPanel"
import TopServicesTable      from "../TopServicesTable"
import BIInsightsPanel       from "../BIInsightsPanel"
import { useDashboardMetrics } from "../../../hooks/useDashboardMetrics"

export default function OverviewTab({ data }) {
  const metrics = useDashboardMetrics(data)
  if (!metrics) return null

  return (
    <div className="space-y-6">
      <KPICardsRow1 data={data} metrics={metrics} />
      <KPICardsRow2 data={data} metrics={metrics} />

      <div className="flex gap-4">
        <SubscriptionDonutChart
          data={metrics.subscriptionPieData}
          total={data.subscriptions.total}
        />
        <ChurnPieChart
          data={metrics.churnPieData}
          churn={data.churn}
          isVoluntaryDominant={metrics.isVoluntaryDominant}
        />
      </div>

      <div className="flex gap-4">
        <TrialDropoffChart data={metrics.dropoffBarData} />
        <EngagementHealthPanel bars={metrics.engagementBars} />
      </div>

      <TopServicesTable services={data.top_services} />
      <BIInsightsPanel insights={metrics.biInsights} />
    </div>
  )
}

OverviewTab.propTypes = {
  data:    PropTypes.object.isRequired,
  filters: PropTypes.object.isRequired,
}