import { useEffect, useRef, useState } from 'react';
import { Mail, Lock } from 'lucide-react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage, getFieldErrors } from '../../utils/errors';

export function LoginForm({ onSuccess, initialEmail = '' }) {
  const { login } = useAuth();
  const [values, setValues] = useState({ email: initialEmail, password: '' });
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);
  const passwordRef = useRef(null);

  // Picking a "recent account" (see RecentAccountsPicker) fills the email
  // and moves focus to the password field — with the autoComplete hints
  // below, that's what prompts the browser's own saved-password manager to
  // offer filling the password in, without us ever storing it ourselves.
  useEffect(() => {
    if (!initialEmail) return;
    setValues((current) => ({ ...current, email: initialEmail }));
    passwordRef.current?.focus();
  }, [initialEmail]);

  function handleChange(field) {
    return (event) => setValues((current) => ({ ...current, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setFormError(null);
    setFieldErrors({});
    try {
      const user = await login(values);
      onSuccess?.(user);
    } catch (error) {
      setFieldErrors(getFieldErrors(error));
      setFormError(getErrorMessage(error, 'Incorrect email or password.'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      {formError && (
        <p role="alert" className="rounded-lg bg-danger-50 px-3 py-2 text-sm text-danger-700">
          {formError}
        </p>
      )}
      <Input
        label="Email address"
        type="email"
        autoComplete="email"
        required
        leftIcon={<Mail className="h-4 w-4" aria-hidden="true" />}
        value={values.email}
        onChange={handleChange('email')}
        error={fieldErrors.email}
      />
      <Input
        label="Password"
        type="password"
        autoComplete="current-password"
        required
        ref={passwordRef}
        leftIcon={<Lock className="h-4 w-4" aria-hidden="true" />}
        value={values.password}
        onChange={handleChange('password')}
        error={fieldErrors.password}
      />
      <Button type="submit" fullWidth loading={loading}>
        Log in
      </Button>
    </form>
  );
}