/**
 * Footer
 * Compact single-line footer bar with copyright and attribution
 * Stays at the bottom of the right column, never covers sidebar
 * @returns {JSX.Element}
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className="flex-shrink-0 px-6 py-3 flex items-center justify-between"
      style={{
        borderTop: "1px solid var(--color-border)",
        backgroundColor: "var(--color-bg-card)",
      }}
    >
      <p className="text-xs" style={{ color: "var(--color-text-muted)" }}>
        © {currentYear} Digmaco . All rights reserved.
      </p>
      <p className="text-xs" style={{ color: "var(--color-text-disabled)" }}>
        Built with DigMaco · IT Analytics Division
      </p>
    </footer>
  );
}
