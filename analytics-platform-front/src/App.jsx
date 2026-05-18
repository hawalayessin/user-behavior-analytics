import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import ForgotPasswordPage from "./pages/auth/ForgotPasswordPage";
import ResetPasswordPage from "./pages/auth/ResetPasswordPage";
import PrivateRoute from "./router/PrivateRoute";
import AdminRoute from "./router/AdminRoute";
import AppLayout from "./components/layout/AppLayout";
import DashboardPage from "./pages/dashboard/DashboardPage";
import RootRedirect from "./pages/RootRedirect";
import PlatformUsersPage from "./pages/platform-users/PlatformUsersPage";
import UserActivityPage from "./pages/UserActivityPage";
import SubscribersPage from "./pages/SubscribersPage";
import FreeTrialBehaviorPage from "./pages/dashboard/FreeTrialBehaviorPage";
import RetentionPage from "./pages/dashboard/RetentionPage";
import ImportDataPage from "./pages/admin/ImportDataPage";
import CampaignImpactPage from "./pages/dashboard/CampaignImpactPage";
import ChurnAnalysisPage from "./pages/dashboard/ChurnAnalysisPage";
import AIChurnInsights from "./pages/dashboard/AIChurnInsights";
import CrossServiceBehaviorPage from "./pages/dashboard/CrossServiceBehaviorPage";
import UserSegmentationPage from "./pages/dashboard/UserSegmentationPage";
import AnomalyDetectionPage from "./pages/dashboard/AnomalyDetectionPage";
import ManagementPage from "./pages/admin/ManagementPage";
import SystemSettingsPage from "./pages/admin/SystemSettingsPage";
import RunAIModelsPage from "./pages/admin/RunAIModelsPage";
import ProfileSettingsPage from "./pages/account/ProfileSettingsPage";
import NotesPage from "./pages/NotesPage";
import ReportGeneratorPage from "./pages/admin/ReportGeneratorPage";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Protected routes — PrivateRoute + AppLayout persist across navigations */}
          <Route element={<PrivateRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<RootRedirect />} />

              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/dashboard-1" element={<DashboardPage />} />
              <Route path="/analytics/behaviors" element={<UserActivityPage />} />
              <Route path="/analytics/trial" element={<FreeTrialBehaviorPage />} />
              <Route path="/analytics/retention" element={<RetentionPage />} />
              <Route path="/analytics/campaigns" element={<CampaignImpactPage />} />
              <Route path="/analytics/churn" element={<ChurnAnalysisPage />} />
              <Route path="/analytics/churn-prediction" element={<AIChurnInsights />} />
              <Route path="/analytics/cross-service" element={<CrossServiceBehaviorPage />} />
              <Route path="/analytics/segmentation" element={<UserSegmentationPage />} />
              <Route path="/analytics/anomalies" element={<AnomalyDetectionPage />} />
              <Route path="/management/subscribers" element={<SubscribersPage />} />
              <Route path="/admin/reports" element={<ReportGeneratorPage />} />
              <Route path="/account/profile" element={<ProfileSettingsPage />} />
              <Route path="/notes" element={<NotesPage />} />

              {/* Admin-only routes */}
              <Route element={<AdminRoute />}>
                <Route path="/admin/users" element={<PlatformUsersPage />} />
                <Route path="/admin/import" element={<ImportDataPage />} />
                <Route path="/admin/management" element={<ManagementPage />} />
                <Route path="/admin/settings" element={<SystemSettingsPage />} />
                <Route path="/admin/run-ai-models" element={<RunAIModelsPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
