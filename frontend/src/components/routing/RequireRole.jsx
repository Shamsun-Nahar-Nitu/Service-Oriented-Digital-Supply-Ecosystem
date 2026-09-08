import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { PageSpinner } from '../ui/Spinner';

/**
 * Gate for role-restricted areas (vendor dashboard, admin console). Assumes
 * <RequireAuth /> already guarantees a logged-in user higher up the route
 * tree — this only adds the role check on top, redirecting mismatched
 * roles to a clear "not allowed" page rather than a blank screen.
 */
export function RequireRole({ roles }) {
  const { user, booting } = useAuth();

  if (booting) return <PageSpinner label="Checking your session…" />;

  if (!user || !roles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}
