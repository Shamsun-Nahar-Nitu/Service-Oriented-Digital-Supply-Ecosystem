import { AUTH_STORAGE_KEY } from '../utils/constants';

/**
 * Thin wrapper around localStorage for the JWT pair + cached user object.
 * Centralized so the refresh interceptor, AuthContext, and axios client can
 * all read/write the same shape without duplicating key names.
 */
function read() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function write(value) {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(value));
}

export const tokenStorage = {
  getAccess() {
    return read()?.access ?? null;
  },
  getRefresh() {
    return read()?.refresh ?? null;
  },
  getUser() {
    return read()?.user ?? null;
  },
  setSession({ access, refresh, user }) {
    const current = read() ?? {};
    write({
      access: access ?? current.access,
      refresh: refresh ?? current.refresh,
      user: user ?? current.user,
    });
  },
  setUser(user) {
    const current = read() ?? {};
    write({ ...current, user });
  },
  clear() {
    localStorage.removeItem(AUTH_STORAGE_KEY);
  },
};
