import React from "react"
import PropTypes from "prop-types"
import { Users, Shield, Wifi, Ban } from "lucide-react"

export default function UserKPICards({
  total,
  administrators,
  activeNow,
  inactiveAccounts,
}) {
  const cards = [
    {
      label: "Total Users",
      value: total,
      icon: Users,
      iconColor: "text-indigo-400",
    },
    {
      label: "Administrators",
      value: administrators,
      icon: Shield,
      iconColor: "text-blue-400",
    },
    {
      label: "Active Now",
      value: activeNow,
      icon: Wifi,
      iconColor: "text-emerald-400",
    },
    {
      label: "Inactive Accounts",
      value: inactiveAccounts,
      icon: Ban,
      iconColor: "text-red-400",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon
        return (
          <div
            key={idx}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden"
          >
            {/* Icon */}
            <div className="absolute top-4 right-4 opacity-20">
              <Icon size={32} className={card.iconColor} />
            </div>

            {/* Content */}
            <div className="relative z-10">
              <p className="text-sm text-slate-500 mb-2">{card.label}</p>
              <p className="text-3xl font-bold text-slate-100">{card.value}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

UserKPICards.propTypes = {
  total: PropTypes.number.isRequired,
  administrators: PropTypes.number.isRequired,
  activeNow: PropTypes.number.isRequired,
  inactiveAccounts: PropTypes.number.isRequired,
}
