import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LoginForm } from '../components/forms/LoginForm';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname ?? '/';

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink-900">Welcome back</h1>
      <p className="mt-1 text-sm text-ink-500">Log in to continue shopping.</p>

      <div className="mt-6">
        <LoginForm onSuccess={() => navigate(from, { replace: true })} />
      </div>

      <p className="mt-6 text-center text-sm text-ink-500">
        New here?{' '}
        <Link to="/register" className="font-medium text-ember-600 hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
