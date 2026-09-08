import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { PageSpinner } from '../ui/Spinner';

/**
 * Gate for any route that needs a logged-in user (cart checkout, orders,
 * profile, dashboards). Sends anonymous visitors to /login and remembers
 * where they were headed via location state, so LoginPage can bounce them
 * back after a successful sign-in instead of dumping them on the homepage.
 */
export function RequireAuth() {
  const { isAuthenticated, booting } = useAuth();
  const location = useLocation();

  if (booting) return <PageSpinner label="Checking your session…" />;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
