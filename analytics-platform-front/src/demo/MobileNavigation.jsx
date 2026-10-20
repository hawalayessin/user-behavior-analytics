import { useLocation, useNavigate } from 'react-router-dom';
import { navigationConfig } from '../components/layout/navConfig';
import { ThemeToggle } from '../components/layout/ThemeToggle';

export default function MobileNavigation() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  return (
    <nav className="md:hidden border-b p-4 space-y-3" style={{ borderColor: 'var(--color-border)' }} aria-label="Demo navigation">
      <div className="flex items-center justify-between">
        <span className="font-bold" style={{ color: 'var(--color-text-primary)' }}>InsightHub</span>
        <ThemeToggle />
      </div>
      <select aria-label="Page" value={pathname} onChange={e => navigate(e.target.value)} className="w-full rounded-md px-3 py-2 text-sm" style={{ backgroundColor: 'var(--color-bg-card)', color: 'var(--color-text-primary)', border: '1px solid var(--color-border)' }}>
        {navigationConfig.map(section => (
          <optgroup key={section.section} label={section.section}>
            {section.items.map(item => <option key={item.route} value={item.route}>{item.label.trim()}</option>)}
          </optgroup>
        ))}
        <option value="/account/profile">Profile</option>
      </select>
    </nav>
  );
}
