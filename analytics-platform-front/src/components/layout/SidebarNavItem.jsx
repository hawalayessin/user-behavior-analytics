import { NavLink } from 'react-router-dom'

/**
 * SidebarNavItem
 * @param {Object} props
 * @param {React.ElementType} props.icon - lucide-react icon component
 * @param {string} props.label - item label text
 * @param {string} props.route - target route path
 * @param {boolean} props.isCollapsed - sidebar collapse state
 */
export default function SidebarNavItem({ icon: IconComponent, label, route, isCollapsed }) {
  const tooltipVisibleClass = isCollapsed ? 'group-hover:visible' : 'invisible'

  return (
    <NavLink
      to={route}
      className={({ isActive }) =>
        `group relative flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
          isActive
            ? 'bg-indigo-500/8 border-l-4 border-indigo-500 text-slate-100'
            : 'text-slate-400 hover:bg-slate-800/60 border-l-4 border-transparent'
        }`
      }
    >
      {({ isActive }) => (
        <>
          <IconComponent
            className={`w-5 h-5 flex-shrink-0 transition-colors duration-200 ${
              isActive ? 'text-indigo-500' : 'text-slate-500 group-hover:text-slate-400'
            }`}
          />
          {!isCollapsed && <span className="text-sm font-medium truncate">{label}</span>}
          
          {isCollapsed && (
            <div
              className={`absolute left-full ml-2 px-3 py-1.5 bg-slate-800 text-slate-200 text-xs whitespace-nowrap rounded shadow-lg pointer-events-none ${tooltipVisibleClass} transition-visibility duration-200`}
            >
              {label}
            </div>
          )}
        </>
      )}
    </NavLink>
  )
}
