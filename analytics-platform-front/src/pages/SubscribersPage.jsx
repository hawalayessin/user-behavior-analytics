import AppLayout from "../components/layout/AppLayout";
import UserListSection from "../components/subscribers/UserListSection";
import { useSubscribersKPIs } from "../hooks/useSubscribersKPIs";

export default function SubscribersPage() {
  const { kpis, loading, error } = useSubscribersKPIs();

  const kpiNewSubscriptions = loading
    ? "..."
    : kpis.newSubscriptions30d.toLocaleString();
  const kpiAtRisk = loading ? "..." : kpis.atRiskUsers.toLocaleString();
  const kpiLoyalty = loading ? "..." : `${kpis.loyaltyScoreAvg.toFixed(1)}%`;
  const kpiArpu = loading ? "..." : kpis.arpuTnd.toFixed(2);
  const kpiUssd = loading ? "..." : kpis.channelUssd.toLocaleString();
  const kpiWeb = loading ? "..." : kpis.channelWeb.toLocaleString();

  return (
    <AppLayout pageTitle="Abonnés">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">
            Subscriber Directory
          </h1>
          <p className="text-sm text-slate-400">
            Manage and monitor customer service lifecycles across the Tunisian
            national network infrastructure.
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-6">
          {/* New Subscriptions */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg
                className="w-[100px] h-[100px]"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0-6c1.1 0 2 .89 2 2s-.89 2-2 2-2-.89-2-2 .89-2 2-2zm0 7c-2.67 0-8 1.34-8 4v3h16v-3c0-2.66-5.33-4-8-4z" />
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              New Subscriptions
            </div>
            <div className="text-3xl font-black text-slate-100 mb-2">
              {kpiNewSubscriptions}
            </div>
            <div className="text-xs text-slate-400 font-medium">
              Last 30 days (backend)
            </div>
          </div>

          {/* USSD Activations */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg
                className="w-[100px] h-[100px]"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M17 1H7c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-2-2-2zm0 18H7V5h10v14z" />
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              USSD Activations
            </div>
            <div className="text-3xl font-black text-slate-100 mb-2">
              {kpiUssd}
            </div>
            <div className="text-xs text-slate-400 font-medium">
              All-time user activation channel
            </div>
          </div>

          {/* Web Activations */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg
                className="w-[100px] h-[100px]"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M4 5h16v10H4V5zm0 12h16v2H4v-2z" />
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              Web Activations
            </div>
            <div className="text-3xl font-black text-slate-100 mb-2">
              {kpiWeb}
            </div>
            <div className="text-xs text-slate-400 font-medium">
              All-time user activation channel
            </div>
          </div>

          {/* Active Risk Threshold */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg
                className="w-[100px] h-[100px]"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              Active Risk Threshold
            </div>
            <div className="text-3xl font-black text-orange-400 mb-2">
              {kpiAtRisk}
            </div>
            <div className="text-xs text-orange-400/60 font-medium">
              Distinct users marked at risk
            </div>
          </div>

          {/* Loyalty Score Avg */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
              <svg
                className="w-[100px] h-[100px]"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              Loyalty Score Avg
            </div>
            <div className="text-3xl font-black text-slate-100 mb-2">
              {kpiLoyalty}
            </div>
            <div className="text-xs text-slate-400 font-medium">
              Stickiness rate from backend engagement
            </div>
          </div>

          {/* Total Directory ARPU */}
          <div className="p-6 bg-slate-800 border border-slate-700 rounded-xl relative overflow-hidden group hover:border-slate-600 transition">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              Total Directory ARPU
            </div>
            <div className="text-3xl font-black text-emerald-400 mb-2">
              {kpiArpu} <span className="text-sm font-normal">TND</span>
            </div>
            <div className="text-xs text-emerald-400/70 font-medium">
              Current month ARPU
            </div>
          </div>
        </div>

        {/* User List Section */}
        <UserListSection />

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            KPI backend unavailable: {error}
          </div>
        )}

        {!loading && !error && kpis.dataAnchor && (
          <div className="text-xs text-slate-500">
            KPI data anchor: {kpis.dataAnchor}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
