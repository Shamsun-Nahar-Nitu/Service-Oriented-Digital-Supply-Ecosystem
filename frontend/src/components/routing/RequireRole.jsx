import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { PageSpinner } from '../ui/Spinner';
import { getHomePath } from '../../utils/roleHome';

/**
 * Gate for role-restricted areas. Assumes <RequireAuth /> already guarantees
 * a logged-in user higher up the route tree — this only adds the role check.
 */
export function RequireRole({ roles }) {
  const { user, booting } = useAuth();

  if (booting) return <PageSpinner label="Checking your session…" />;

  if (!user || !roles.includes(user.role)) {
    return <Navigate to={getHomePath(user?.role)} replace />;
  }

  return <Outlet />;
}
