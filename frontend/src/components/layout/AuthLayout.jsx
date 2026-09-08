import { Link, Outlet } from 'react-router-dom';
import { Store } from 'lucide-react';

const APP_NAME = import.meta.env.VITE_APP_NAME || 'ShopNest';

/** Minimal centered shell for /login and /register — no header, cart, or nav chrome. */
export function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-ink-900 px-4 py-12">
      <Link to="/" className="mb-8 flex items-center gap-2 font-display text-xl font-bold text-white">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-ember-500 text-white">
          <Store className="h-5 w-5" aria-hidden="true" />
        </span>
        {APP_NAME}
      </Link>
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-popover sm:p-8">
        <Outlet />
      </div>
    </div>
  );
}
