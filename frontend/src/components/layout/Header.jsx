import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShoppingCart,
  User,
  Menu,
  X,
  ClipboardList,
  LogOut,
  Settings,
  Store,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';
import { SearchBar } from './SearchBar';
import { DropdownMenu, DropdownMenuItem, DropdownMenuSeparator } from '../ui/DropdownMenu';
import { ROLE_LABELS } from '../../utils/constants';
import { getHomePath } from '../../utils/roleHome';
import { cn } from '../../utils/cn';

const APP_NAME = import.meta.env.VITE_APP_NAME || 'ShopNest';

const NAV_LINKS = [
  { to: '/', label: 'Home' },
  { to: '/products', label: 'All Products' },
];

export function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const { itemCount } = useCart();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <header className="sticky top-0 z-30 bg-ink-900 text-white">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6">
        <button
          type="button"
          className="rounded-md p-1.5 hover:bg-white/10 lg:hidden"
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen((current) => !current)}
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>

        <Link to="/" className="flex shrink-0 items-center gap-2 font-display text-lg font-bold">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ember-500 text-white">
            <Store className="h-4 w-4" aria-hidden="true" />
          </span>
          {APP_NAME}
        </Link>

        <nav className="hidden items-center gap-1 lg:flex" aria-label="Primary">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="rounded-md px-3 py-2 text-sm font-medium text-ink-100 hover:bg-white/10"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden flex-1 md:block">
          <SearchBar />
        </div>

        <div className="ml-auto flex items-center gap-1.5 sm:gap-2">
          {isAuthenticated && user.role === 'CUSTOMER' && (
            <Link
              to="/cart"
              aria-label={`Cart, ${itemCount} item${itemCount === 1 ? '' : 's'}`}
              className="relative flex h-10 w-10 items-center justify-center rounded-lg hover:bg-white/10"
            >
              <ShoppingCart className="h-5 w-5" aria-hidden="true" />
              {itemCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-ember-500 px-1 text-[11px] font-bold text-white">
                  {itemCount > 99 ? '99+' : itemCount}
                </span>
              )}
            </Link>
          )}

          {isAuthenticated ? (
            <DropdownMenu
              align="right"
              className="flex h-10 items-center gap-2 rounded-lg px-2 hover:bg-white/10 sm:px-3"
              trigger={
                <>
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-ember-500 text-xs font-bold">
                    {user.first_name?.[0]?.toUpperCase() ?? <User className="h-4 w-4" />}
                  </span>
                  <span className="hidden text-sm font-medium sm:inline">{user.first_name}</span>
                </>
              }
            >
              <div className="px-3 py-2">
                <p className="truncate text-sm font-semibold text-ink-900">{user.full_name || user.email}</p>
                <p className="text-xs text-ink-500">{ROLE_LABELS[user.role]}</p>
              </div>
              <DropdownMenuSeparator />
              {user.role === 'CUSTOMER' && (
                <DropdownMenuItem as={Link} to="/cart">
                  <ShoppingCart className="h-4 w-4" aria-hidden="true" /> Cart
                </DropdownMenuItem>
              )}
              {user.role === 'VENDOR' && (
                <DropdownMenuItem as={Link} to={getHomePath(user.role)}>
                  <Store className="h-4 w-4" aria-hidden="true" /> Vendor panel
                </DropdownMenuItem>
              )}
              {(user.role === 'ADMIN' || user.role === 'MANAGER') && (
                <DropdownMenuItem as={Link} to={getHomePath(user.role)}>
                  <Settings className="h-4 w-4" aria-hidden="true" /> Management
                </DropdownMenuItem>
              )}
              {user.role === 'CUSTOMER' && (
                <DropdownMenuItem as={Link} to="/orders">
                  <ClipboardList className="h-4 w-4" aria-hidden="true" /> My orders
                </DropdownMenuItem>
              )}
              <DropdownMenuItem as={Link} to="/profile">
                <Settings className="h-4 w-4" aria-hidden="true" /> Profile settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-danger-600 hover:bg-danger-50">
                <LogOut className="h-4 w-4" aria-hidden="true" /> Log out
              </DropdownMenuItem>
            </DropdownMenu>
          ) : (
            <div className="hidden items-center gap-2 sm:flex">
              <Link
                to="/login"
                className="rounded-lg px-3 py-2 text-sm font-medium text-white hover:bg-white/10"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="rounded-lg bg-ember-500 px-3 py-2 text-sm font-semibold text-white hover:bg-ember-600"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </div>

      <div className="px-4 pb-3 md:hidden">
        <SearchBar />
      </div>

      {mobileOpen && (
        <div className="border-t border-white/10 bg-ink-900 px-4 py-3 lg:hidden">
          <nav className="flex flex-col gap-1" aria-label="Mobile">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileOpen(false)}
                className="rounded-md px-3 py-2.5 text-sm font-medium text-ink-100 hover:bg-white/10"
              >
                {link.label}
              </Link>
            ))}
            {isAuthenticated && user.role === 'CUSTOMER' && (
              <>
                <Link to="/cart" onClick={() => setMobileOpen(false)} className="rounded-md px-3 py-2.5 text-sm font-medium text-ink-100 hover:bg-white/10">Cart</Link>
                <Link to="/orders" onClick={() => setMobileOpen(false)} className="rounded-md px-3 py-2.5 text-sm font-medium text-ink-100 hover:bg-white/10">Orders</Link>
              </>
            )}
            {isAuthenticated && user.role === 'VENDOR' && (
              <Link to={getHomePath(user.role)} onClick={() => setMobileOpen(false)} className="rounded-md px-3 py-2.5 text-sm font-medium text-ink-100 hover:bg-white/10">Vendor panel</Link>
            )}
            {isAuthenticated && (user.role === 'ADMIN' || user.role === 'MANAGER') && (
              <Link to={getHomePath(user.role)} onClick={() => setMobileOpen(false)} className="rounded-md px-3 py-2.5 text-sm font-medium text-ink-100 hover:bg-white/10">Management</Link>
            )}
            {!isAuthenticated && (
              <div className={cn('mt-2 flex gap-2 border-t border-white/10 pt-3')}>
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="flex-1 rounded-lg border border-white/20 px-3 py-2 text-center text-sm font-medium"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileOpen(false)}
                  className="flex-1 rounded-lg bg-ember-500 px-3 py-2 text-center text-sm font-semibold"
                >
                  Sign up
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}