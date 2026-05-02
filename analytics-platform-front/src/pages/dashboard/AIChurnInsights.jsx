import AppLayout from "../../components/layout/AppLayout";
import ChurnPredictionDashboard from "../../components/dashboard/churn_prediction/churn_dashboard";

export default function AIChurnInsights() {
  return (
    <AppLayout
      pageTitle="Churn Prediction"
      hasNotifications={false}
      showExportButton={false}
    >
      <div className="space-y-6">
        <div>
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: "var(--color-text-primary)" }}
          >
            AI Churn Prediction
          </h1>
          <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
            Logistic Regression model that estimates churn risk for active
            subscriptions.
          </p>
        </div>

        <ChurnPredictionDashboard />
      </div>
    </AppLayout>
  );
}
