import PropTypes from "prop-types"

const TABS = [
  { index: 0, label: "Overview"               },
  { index: 1, label: "Engagement"             },
  { index: 2, label: "Subscriptions & Revenue"},
  { index: 3, label: "Free Trial & Churn"     },
]

export default function TabNavigation({ activeTab, onTabChange }) {
  return (
    <div className="flex gap-1 p-1 bg-[#1A1D27] border border-slate-800 rounded-xl w-fit">
      {TABS.map((tab) => (
        <button
          key={tab.index}
          onClick={() => onTabChange(tab.index)}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
            activeTab === tab.index
              ? "bg-violet-700 text-white shadow"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

TabNavigation.propTypes = {
  activeTab:   PropTypes.number.isRequired,
  onTabChange: PropTypes.func.isRequired,
}