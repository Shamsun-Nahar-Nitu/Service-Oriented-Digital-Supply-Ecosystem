import { X } from 'lucide-react';

function initials(name) {
  const parts = name.split(' ').filter(Boolean).slice(0, 2);
  return parts.map((part) => part[0].toUpperCase()).join('') || '?';
}

/**
 * Shows the device's recently-used accounts (see utils/recentAccounts) so
 * returning users can jump straight to the password step instead of
 * retyping their email every time. Clicking an account only fills the
 * email — see LoginForm for why the password is never pre-filled by us.
 */
export function RecentAccountsPicker({ accounts, onSelect, onRemove }) {
  if (accounts.length === 0) return null;

  return (
    <div className="mb-6">
      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-ink-500">
        Recent accounts
      </p>
      <ul className="space-y-2">
        {accounts.map((account) => (
          <li
            key={account.email}
            className="flex items-center gap-2 rounded-lg border border-ink-200 bg-white pr-2 transition-colors hover:border-ember-300 hover:bg-ember-50"
          >
            <button
              type="button"
              onClick={() => onSelect(account.email)}
              className="flex flex-1 items-center gap-3 px-3 py-2.5 text-left"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink-100 text-sm font-semibold text-ink-700">
                {initials(account.name)}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-medium text-ink-900">
                  {account.name}
                </span>
                <span className="block truncate text-xs text-ink-500">{account.email}</span>
              </span>
            </button>
            <button
              type="button"
              onClick={() => onRemove(account.email)}
              aria-label={`Remove ${account.email} from recent accounts`}
              className="shrink-0 rounded-md p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-600"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </li>
        ))}
      </ul>
      <div className="mt-4 flex items-center gap-3 text-xs text-ink-400">
        <span className="h-px flex-1 bg-ink-100" />
        or use a different account
        <span className="h-px flex-1 bg-ink-100" />
      </div>
    </div>
  );
}