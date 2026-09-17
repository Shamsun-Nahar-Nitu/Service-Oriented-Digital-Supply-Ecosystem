import { Link } from 'react-router-dom';
import { Store } from 'lucide-react';

const APP_NAME = import.meta.env.VITE_APP_NAME || 'ShopNest';

export function Footer() {
  return (
    <footer className="border-t border-ink-100 bg-white">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-3">
        <div>
          <Link to="/" className="flex items-center gap-2 font-display text-lg font-bold text-ink-900">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ember-500 text-white">
              <Store className="h-4 w-4" aria-hidden="true" />
            </span>
            {APP_NAME}
          </Link>
          <p className="mt-3 max-w-xs text-sm text-ink-500">
            A multi-vendor marketplace where independent sellers list their catalog and shoppers
            check out in one place.
          </p>
        </div>

        <FooterColumn
          title="Shop"
          links={[
            { to: '/products', label: 'All products' },
            { to: '/products?in_stock=true', label: 'In stock now' },
            { to: '/orders', label: 'Track an order' },
          ]}
        />
        <FooterColumn
          title="Account"
          links={[
            { to: '/profile', label: 'Profile settings' },
          ]}
        />
      </div>
      <div className="border-t border-ink-100 px-4 py-4 text-center text-xs text-ink-400 sm:px-6">
        © {new Date().getFullYear()} {APP_NAME}. All rights reserved. · Developed by <a href="https://github.com/Shamsun-Nahar-Nitu" target="_blank" rel="noopener noreferrer">Shamsun Nahar</a>.
      </div>
    </footer>
  );
}

function FooterColumn({ title, links }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-ink-900">{title}</h3>
      <ul className="mt-3 flex flex-col gap-2">
        {links.map((link) => (
          <li key={link.to}>
            <Link to={link.to} className="text-sm text-ink-500 hover:text-ink-800">
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
