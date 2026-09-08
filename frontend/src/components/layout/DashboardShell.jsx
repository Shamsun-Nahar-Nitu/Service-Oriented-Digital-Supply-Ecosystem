import { NavLink, Outlet, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { cn } from '../../utils/cn';

/**
 * Shared shell for the vendor and admin areas: a sidebar of nav links plus
 * a topbar with a way back to the storefront. VendorLayout and AdminLayout
 * each just supply their own `navItems` and `title` — the chrome is common.
 */
export function DashboardShell({ title, navItems }) {
  return (
    <div className="flex min-h-screen flex-col bg-canvas lg:flex-row">
      <aside className="border-b border-ink-100 bg-ink-900 text-white lg:w-64 lg:shrink-0 lg:border-b-0">
        <div className="flex items-center justify-between px-4 py-4 lg:flex-col lg:items-start lg:gap-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-ink-300">Dashboard</p>
            <h2 className="font-display text-lg font-bold">{title}</h2>
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-2 pb-3 no-scrollbar lg:flex-col lg:overflow-visible lg:px-3 lg:pb-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  'flex shrink-0 items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive ? 'bg-white/10 text-white' : 'text-ink-300 hover:bg-white/5 hover:text-white'
                )
              }
            >
              <item.icon className="h-4 w-4" aria-hidden="true" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="hidden border-t border-white/10 px-3 py-3 lg:block">
          <Link
            to="/"
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-ink-300 hover:bg-white/5 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Back to store
          </Link>
        </div>
      </aside>
      <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
