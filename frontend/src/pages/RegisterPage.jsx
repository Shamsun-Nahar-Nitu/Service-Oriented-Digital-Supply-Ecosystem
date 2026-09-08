import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import { RegisterForm } from '../components/forms/RegisterForm';
import { Button } from '../components/ui/Button';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [registeredEmail, setRegisteredEmail] = useState(null);

  if (registeredEmail) {
    return (
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-success-100 text-success-600">
          <CheckCircle2 className="h-6 w-6" aria-hidden="true" />
        </span>
        <h1 className="font-display text-xl font-bold text-ink-900">Account created</h1>
        <p className="text-sm text-ink-500">
          {registeredEmail} is ready to go — log in to start shopping.
        </p>
        <Button onClick={() => navigate('/login')} className="mt-2" fullWidth>
          Continue to log in
        </Button>
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink-900">Create your account</h1>
      <p className="mt-1 text-sm text-ink-500">Shop the marketplace, or list products as a vendor.</p>

      <div className="mt-6">
        <RegisterForm onSuccess={setRegisteredEmail} />
      </div>

      <p className="mt-6 text-center text-sm text-ink-500">
        Already have an account?{' '}
        <Link to="/login" className="font-medium text-ember-600 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
