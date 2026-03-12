/**
 * Footer
 * Compact single-line footer bar with copyright and attribution
 * Stays at the bottom of the right column, never covers sidebar
 * @returns {JSX.Element}
 */
export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="flex-shrink-0 border-t border-slate-800 bg-slate-900/50 px-6 py-3 flex items-center justify-between">
      <p className="text-xs text-slate-500">
        © {currentYear} Digmaco . All rights reserved.
      </p>
      <p className="text-xs text-slate-600">
        Built with DigMaco · IT Analytics Division
      </p>
    </footer>
  )
}
