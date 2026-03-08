import Sidebar from './Sidebar'
import Topbar from './Topbar'
import Footer from './Footer'

/**
 * AppLayout
 * Full page layout wrapper: Sidebar (fixed width) + Right column (Topbar + Content + Footer)
 * Ensures sidebar is always visible and footer stays inside the right column
 * @param {Object} props
 * @param {React.ReactNode} props.children - page content
 * @param {string} props.pageTitle - current page title for breadcrumb
 * @param {boolean} props.hasNotifications - show notifications badge
 * @param {boolean} props.showExportButton - display export button
 */
export default function AppLayout({
  children,
  pageTitle = 'Dashboard',
  hasNotifications = false,
  showExportButton = false,
}) {
  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      {/* Sidebar — always visible, never covered */}
      <Sidebar />

      {/* Right column — flex column with topbar, content, footer */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Topbar */}
        <Topbar
          pageTitle={pageTitle}
          hasNotifications={hasNotifications}
          showExportButton={showExportButton}
        />

        {/* Main scrollable content area */}
        <main className="flex-1 overflow-y-auto px-6 py-6 scrollbar-modern">
          {children}
        </main>

        {/* Footer — stays at bottom of right column */}
        <Footer />
      </div>
    </div>
  )
}
