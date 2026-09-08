import { useState } from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { authApi } from '../../api/auth';
import { useToast } from '../../context/ToastContext';
import { getErrorMessage, getFieldErrors } from '../../utils/errors';

const EMPTY_VALUES = { old_password: '', new_password: '', confirm_password: '' };

export function ChangePasswordForm() {
  const toast = useToast();
  const [values, setValues] = useState(EMPTY_VALUES);
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function handleChange(field) {
    return (event) => setValues((current) => ({ ...current, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setFieldErrors({});

    if (values.new_password !== values.confirm_password) {
      setFieldErrors({ confirm_password: 'Passwords do not match.' });
      setLoading(false);
      return;
    }

    try {
      await authApi.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      });
      toast.success('Password changed successfully.');
      setValues(EMPTY_VALUES);
    } catch (error) {
      setFieldErrors(getFieldErrors(error));
      toast.error(getErrorMessage(error, 'Could not change your password.'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <Input
        label="Current password"
        type="password"
        required
        autoComplete="current-password"
        value={values.old_password}
        onChange={handleChange('old_password')}
        error={fieldErrors.old_password}
      />
      <Input
        label="New password"
        type="password"
        required
        autoComplete="new-password"
        value={values.new_password}
        onChange={handleChange('new_password')}
        error={fieldErrors.new_password}
      />
      <Input
        label="Confirm new password"
        type="password"
        required
        autoComplete="new-password"
        value={values.confirm_password}
        onChange={handleChange('confirm_password')}
        error={fieldErrors.confirm_password}
      />
      <Button type="submit" loading={loading} className="self-start">
        Update password
      </Button>
    </form>
  );
}
