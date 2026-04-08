import AppLayout from "../components/layout/AppLayout"
import UserListSection from "../components/subscribers/UserListSection"

export default function SubscribersPage() {
  return (
    <AppLayout pageTitle="Abonnés">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Subscriber Directory</h1>
          <p className="text-sm text-slate-400">
            Manage and monitor customer service lifecycles across the Tunisian national network infrastructure.
          </p>
        </div>

        {/* User List Section */}
        <UserListSection />

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* New Subscriptions */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg className="w-[100px] h-[100px]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0-6c1.1 0 2 .89 2 2s-.89 2-2 2-2-.89-2-2 .89-2 2-2zm0 7c-2.67 0-8 1.34-8 4v3h16v-3c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">New Subscriptions</div>
            <div className="text-3xl font-black text-slate-100 mb-2">1,248</div>
            <div className="text-xs text-emerald-400 flex items-center gap-1 font-bold">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M16 6l2.29 2.29-4.29 4.29 4 4-2.29 2.29L12 14.58l-4 4 2.29 2.29L12 19.16l4.29-4.29L16 18V6z"/>
              </svg>
              +14.2% MoM
            </div>
          </div>

          {/* Active Risk Threshold */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg className="w-[100px] h-[100px]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Active Risk Threshold</div>
            <div className="text-3xl font-black text-orange-400 mb-2">421</div>
            <div className="text-xs text-orange-400/60 font-medium">
              Manual intervention required
            </div>
          </div>

          {/* Loyalty Score Avg */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg className="w-[100px] h-[100px]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Loyalty Score Avg</div>
            <div className="text-3xl font-black text-slate-100 mb-2">74.2</div>
            <div className="text-xs text-slate-400 font-medium">
              Above market benchmark (68)
            </div>
          </div>

          {/* Total Directory ARPU */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg className="w-[100px] h-[100px]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Total Directory ARPU</div>
            <div className="text-3xl font-black text-emerald-400 mb-2">89.4 <span className="text-sm font-normal">TND</span></div>
            <div className="text-xs text-emerald-400 flex items-center gap-1 font-bold">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M16 6l2.29 2.29-4.29 4.29 4 4-2.29 2.29L12 14.58l-4 4 2.29 2.29L12 19.16l4.29-4.29L16 18V6z"/>
              </svg>
              +2.1%
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
