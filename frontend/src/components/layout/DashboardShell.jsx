import { NavLink, Outlet, Link, useNavigate } from 'react-router-dom';
import { Settings, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { DropdownMenu, DropdownMenuItem, DropdownMenuSeparator } from '../ui/DropdownMenu';
import { ROLE_LABELS } from '../../utils/constants';
import { cn } from '../../utils/cn';

const APP_NAME = import.meta.env.VITE_APP_NAME || 'ShopNest';

/**
 * Shared shell for the vendor and admin areas: a sidebar of nav links plus
 * a topbar with the account menu. VendorLayout and AdminLayout each just
 * supply their own `navItems` and `title` — the chrome is common.
 */
export function DashboardShell({ title, navItems }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="flex min-h-screen flex-col bg-canvas lg:flex-row">
      <aside className="border-b border-ink-100 bg-ink-900 text-white lg:w-64 lg:shrink-0 lg:border-b-0">
        <div className="px-4 py-4">
          <Link to={navItems[0]?.to ?? '/'} className="font-display text-base font-bold text-white">
            {APP_NAME}
          </Link>
          <p className="mt-0.5 text-xs font-medium uppercase tracking-wide text-ink-300">{title}</p>
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
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex justify-end border-b border-ink-100 bg-white px-4 py-2.5 sm:px-6 lg:px-8">
          <DropdownMenu
            align="right"
            className="flex h-9 items-center gap-2 rounded-lg px-2 hover:bg-ink-100"
            trigger={
              <>
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-ink-900 text-xs font-bold text-white">
                  {user.first_name?.[0]?.toUpperCase() ?? '?'}
                </span>
                <span className="hidden text-sm font-medium text-ink-800 sm:inline">{user.first_name}</span>
              </>
            }
          >
            <div className="px-3 py-2">
              <p className="truncate text-sm font-semibold text-ink-900">{user.full_name || user.email}</p>
              <p className="text-xs text-ink-500">{ROLE_LABELS[user.role]}</p>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem as={Link} to="/profile">
              <Settings className="h-4 w-4" aria-hidden="true" /> Profile settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-danger-600 hover:bg-danger-50">
              <LogOut className="h-4 w-4" aria-hidden="true" /> Log out
            </DropdownMenuItem>
          </DropdownMenu>
        </header>

        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
