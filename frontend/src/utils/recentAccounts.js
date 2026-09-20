const STORAGE_KEY = 'shopnest.recentAccounts';
const MAX_ACCOUNTS = 5;

/**
 * A device-local "recent accounts" list for the login page's quick-switch
 * picker. Deliberately stores only what's needed to identify an account
 * and pre-fill the email field — never a password, token, or anything else
 * sensitive. The browser's own saved-password manager is what actually
 * offers to fill the password once the email is set and the field is
 * focused (see LoginForm's autoComplete attributes); this list only saves
 * the customer from retyping their email.
 */
export function getRecentAccounts() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

/** Call after a successful login. Moves this account to the front, drops
 * any earlier entry for the same email, and caps the list. */
export function rememberAccount(user) {
  if (!user?.email) return;
  try {
    const rest = getRecentAccounts().filter((account) => account.email !== user.email);
    const entry = {
      email: user.email,
      name: user.full_name || user.email,
      role: user.role,
      lastLoginAt: Date.now(),
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify([entry, ...rest].slice(0, MAX_ACCOUNTS)));
  } catch {
    // localStorage can throw in private-browsing/locked-down contexts —
    // this is a convenience feature, so failing silently is fine.
  }
}

/** Removes one account from the picker ("Not you?"). Returns the updated list. */
export function forgetAccount(email) {
  const updated = getRecentAccounts().filter((account) => account.email !== email);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch {
    // Nothing to do if storage is unavailable — the in-memory list below
    // still reflects the removal for the current page view.
  }
  return updated;
}