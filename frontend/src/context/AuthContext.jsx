import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { authApi } from '../api/auth';
import { tokenStorage } from '../api/tokenStorage';
import { STAFF_ROLES } from '../utils/constants';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => tokenStorage.getUser());
  // `booting` covers the one-time startup check that re-validates a cached
  // session against the API; route guards wait on this so they don't bounce
  // an already-logged-in person to /login for a single frame on refresh.
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      if (!tokenStorage.getAccess()) {
        setBooting(false);
        return;
      }
      try {
        const profile = await authApi.fetchProfile();
        if (!cancelled) {
          tokenStorage.setUser(profile);
          setUser(profile);
        }
      } catch {
        if (!cancelled) {
          tokenStorage.clear();
          setUser(null);
        }
      } finally {
        if (!cancelled) setBooting(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (credentials) => {
    const data = await authApi.login(credentials);
    tokenStorage.setSession({ access: data.access, refresh: data.refresh, user: data.user });
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (payload) => {
    return authApi.register(payload);
  }, []);

  const logout = useCallback(() => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (payload) => {
    const updated = await authApi.updateProfile(payload);
    tokenStorage.setUser(updated);
    setUser(updated);
    return updated;
  }, []);

  const value = useMemo(
    () => ({
      user,
      booting,
      isAuthenticated: Boolean(user),
      isStaff: Boolean(user && STAFF_ROLES.includes(user.role)),
      isVendor: user?.role === 'VENDOR',
      isCustomer: user?.role === 'CUSTOMER',
      isAdmin: user?.role === 'ADMIN',
      login,
      register,
      logout,
      updateProfile,
    }),
    [user, booting, login, register, logout, updateProfile]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider.');
  }
  return context;
}
