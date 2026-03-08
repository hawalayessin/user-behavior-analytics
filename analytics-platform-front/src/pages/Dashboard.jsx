import { useAuth } from '../context/AuthContext'
import AppLayout from '../components/layout/AppLayout'

export default function Dashboard() {
  const { full_name, role } = useAuth()

  return (
    <AppLayout pageTitle="Dashboard" hasNotifications={true} showExportButton={true}>
      <div className="px-8 py-8">
        <div className="bg-slate-900 rounded-lg p-8 border border-slate-800">
          <h2 className="text-2xl font-bold text-slate-100 mb-4">
            Bienvenue {full_name}!
          </h2>
          <div className="space-y-2 text-slate-300">
            <p>
              <span className="font-semibold">Rôle:</span> {role}
            </p>
            <p className="text-sm text-slate-500 mt-4">
              Vous êtes connecté à la plateforme analytics.
            </p>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
