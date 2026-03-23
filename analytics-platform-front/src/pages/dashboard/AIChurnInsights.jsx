import AppLayout from "../../components/layout/AppLayout"
import ChurnPredictionDashboard from "../../components/dashboard/churn_prediction/churn_dashboard"

export default function AIChurnInsights() {
  return (
    <AppLayout pageTitle="Churn Prediction" hasNotifications={false} showExportButton={false}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">AI Churn Prediction</h1>
          <p className="text-sm text-slate-400">
            Logistic Regression model that estimates churn risk for active subscriptions.
          </p>
        </div>

        <ChurnPredictionDashboard />
      </div>
    </AppLayout>
  )
}

