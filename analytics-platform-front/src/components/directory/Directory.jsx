import { Search, FolderOpen } from 'lucide-react'
import { useState, useMemo } from 'react'
import { navigationConfig } from '../layout/navConfig'
import { useAuth } from '../../context/AuthContext'

/**
 * Directory
 * Displays a searchable directory of all available navigation routes
 * Admin-only sections are conditionally rendered based on user role
 */
export default function Directory() {
  const [searchQuery, setSearchQuery] = useState('')
  const { isAdmin } = useAuth()

  const allItems = useMemo(() => {
    return navigationConfig
      .filter((section) => !section.adminOnly || isAdmin())
      .flatMap((section) =>
        section.items.map((item) => ({
          ...item,
          section: section.section,
        }))
      )
  }, [isAdmin()])

  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return allItems

    const query = searchQuery.toLowerCase()
    return allItems.filter(
      (item) =>
        item.label.toLowerCase().includes(query) ||
        item.section.toLowerCase().includes(query) ||
        item.route.toLowerCase().includes(query)
    )
  }, [searchQuery, allItems])

  const groupedItems = useMemo(() => {
    return filteredItems.reduce((acc, item) => {
      const section = acc.find((s) => s.section === item.section)
      if (section) {
        section.items.push(item)
      } else {
        acc.push({ section: item.section, items: [item] })
      }
      return acc
    }, [])
  }, [filteredItems])

  return (
    <div className="max-w-2xl mx-auto p-6 bg-slate-950 min-h-screen">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Navigation Directory</h1>
          <p className="text-slate-400">Browse all available sections and routes</p>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500 w-5 h-5" />
          <input
            type="text"
            placeholder="Search routes, sections..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors duration-200"
          />
        </div>

        {filteredItems.length === 0 ? (
          <div className="text-center py-12">
            <FolderOpen className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No routes found matching your search</p>
          </div>
        ) : (
          <div className="space-y-6">
            {groupedItems.map((group) => (
              <div key={group.section} className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden">
                <div className="px-6 py-4 bg-slate-800/50 border-b border-slate-700">
                  <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-widest">
                    {group.section}
                  </h2>
                </div>
                <div className="divide-y divide-slate-800">
                  {group.items.map((item) => {
                    const IconComponent = item.icon
                    return (
                      <div
                        key={item.route}
                        className="px-6 py-4 hover:bg-slate-800/50 transition-colors duration-200"
                      >
                        <div className="flex items-start gap-4">
                          <IconComponent className="w-5 h-5 text-indigo-500 flex-shrink-0 mt-1" />
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-medium text-slate-100">{item.label}</h3>
                            <p className="text-xs text-slate-500 mt-1 font-mono">{item.route}</p>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-slate-900/50 border border-slate-800 rounded-lg text-xs text-slate-400">
          <p>
            <span className="font-semibold text-slate-300">{filteredItems.length}</span> route
            {filteredItems.length !== 1 ? 's' : ''} found
          </p>
        </div>
      </div>
    </div>
  )
}
