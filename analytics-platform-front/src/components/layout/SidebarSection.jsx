/**
 * SidebarSection
 * Groups navigation items under a collapsible section label
 * @param {Object} props
 * @param {string} props.title - section label (uppercase)
 * @param {React.ReactNode} props.children - nav items
 * @param {boolean} props.isCollapsed - sidebar collapse state
 */
export default function SidebarSection({ title, children, isCollapsed }) {
  return (
    <div className="py-4">
      {!isCollapsed && (
        <h3 className="px-4 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-widest">
          {title}
        </h3>
      )}
      <div className="space-y-1">
        {children}
      </div>
    </div>
  )
}
