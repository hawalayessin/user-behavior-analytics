import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import LoginPage from './pages/auth/LoginPage'
import PrivateRoute from './router/PrivateRoute'
import AdminRoute from './router/AdminRoute'
import DashboardPage from './pages/dashboard/DashboardPage'
import RootRedirect from './pages/RootRedirect'
import PlatformUsersPage from './pages/platform-users/PlatformUsersPage'
import UserActivityPage from './pages/UserActivityPage'
import SubscribersPage from './pages/SubscribersPage'
import FreeTrialBehaviorPage from './pages/dashboard/FreeTrialBehaviorPage'
import RetentionPage from './pages/dashboard/RetentionPage'
import ImportDataPage from './pages/admin/ImportDataPage'
import CampaignImpactPage from './pages/dashboard/CampaignImpactPage'
import ChurnAnalysisPage from './pages/dashboard/ChurnAnalysisPage'
import AIChurnInsights from './pages/dashboard/AIChurnInsights'
import CrossServiceBehaviorPage from './pages/dashboard/CrossServiceBehaviorPage'
import UserSegmentationPage from './pages/dashboard/UserSegmentationPage'
import AnomalyDetectionPage from './pages/dashboard/AnomalyDetectionPage'
import ManagementPage from './pages/admin/ManagementPage'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={<PrivateRoute><DashboardPage /></PrivateRoute>}
          />
          <Route
            path="/dashboard-1"
            element={<PrivateRoute><DashboardPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/behaviors"
            element={<PrivateRoute><UserActivityPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/trial"
            element={<PrivateRoute><FreeTrialBehaviorPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/retention"
            element={<PrivateRoute><RetentionPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/campaigns"
            element={<PrivateRoute><CampaignImpactPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/churn"
            element={<PrivateRoute><ChurnAnalysisPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/churn-prediction"
            element={<PrivateRoute><AIChurnInsights /></PrivateRoute>}
          />
          <Route
            path="/analytics/cross-service"
            element={<PrivateRoute><CrossServiceBehaviorPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/segmentation"
            element={<PrivateRoute><UserSegmentationPage /></PrivateRoute>}
          />
          <Route
            path="/analytics/anomalies"
            element={<PrivateRoute><AnomalyDetectionPage /></PrivateRoute>}
          />
          <Route
            path="/management/subscribers"
            element={<PrivateRoute><SubscribersPage /></PrivateRoute>}
          />
          <Route
            path="/admin/users"
            element={<AdminRoute><PlatformUsersPage /></AdminRoute>}
          />
          <Route
            path="/admin/import"
            element={<AdminRoute><ImportDataPage /></AdminRoute>}
          />
          <Route
            path="/admin/management"
            element={<AdminRoute><ManagementPage /></AdminRoute>}
          />
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
