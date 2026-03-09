import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import LoginPage from './pages/auth/LoginPage'
import PrivateRoute from './router/PrivateRoute'
import AdminRoute from './router/AdminRoute'
import Dashboard from './pages/Dashboard'
import RootRedirect from './pages/RootRedirect'
import PlatformUsersPage from './pages/platform-users/PlatformUsersPage'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/admin/users" element={<AdminRoute><PlatformUsersPage /></AdminRoute>} />
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
