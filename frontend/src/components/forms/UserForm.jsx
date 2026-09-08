import { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Select } from '../ui/Select';
import { Checkbox } from '../ui/Checkbox';
import { Button } from '../ui/Button';
import { ROLE_LABELS } from '../../utils/constants';
import { getErrorMessage, getFieldErrors } from '../../utils/errors';

const ROLE_OPTIONS = Object.entries(ROLE_LABELS).map(([value, label]) => ({ value, label }));

function toFormValues(user) {
  return {
    email: user?.email ?? '',
    first_name: user?.first_name ?? '',
    last_name: user?.last_name ?? '',
    phone_number: user?.phone_number ?? '',
    address: user?.address ?? '',
    role: user?.role ?? 'CUSTOMER',
    is_active: user?.is_active ?? true,
    password: '',
  };
}

/**
 * Admin-only account management form (/auth/users/). Unlike self-registration,
 * every role is available here — this is how Manager and Admin accounts get
 * created at all, since RegisterSerializer deliberately refuses those roles.
 */
export function UserForm({ user, onSubmit }) {
  const isEdit = Boolean(user);
  const [values, setValues] = useState(() => toFormValues(user));
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(field) {
    return (event) => {
      const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
      setValues((current) => ({ ...current, [field]: value }));
    };
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setFieldErrors({});

    const payload = { ...values };
    if (isEdit && !payload.password) delete payload.password;
    if (isEdit) delete payload.email; // email is effectively the username; keep it out of PATCH payloads.

    try {
      await onSubmit(payload);
    } catch (error) {
      setFieldErrors(getFieldErrors(error));
      setFormError(getErrorMessage(error, 'Could not save this account.'));
    } finally {
      setSubmitting(false);
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
        required
        disabled={isEdit}
        value={values.email}
        onChange={handleChange('email')}
        error={fieldErrors.email}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          label="First name"
          required
          value={values.first_name}
          onChange={handleChange('first_name')}
          error={fieldErrors.first_name}
        />
        <Input
          label="Last name"
          required
          value={values.last_name}
          onChange={handleChange('last_name')}
          error={fieldErrors.last_name}
        />
      </div>

      <Input
        label="Phone number"
        type="tel"
        value={values.phone_number}
        onChange={handleChange('phone_number')}
        error={fieldErrors.phone_number}
      />
      <Textarea label="Address" rows={2} value={values.address} onChange={handleChange('address')} error={fieldErrors.address} />

      <Select label="Role" options={ROLE_OPTIONS} value={values.role} onChange={handleChange('role')} error={fieldErrors.role} />

      <Input
        label={isEdit ? 'Reset password (optional)' : 'Password'}
        type="password"
        required={!isEdit}
        value={values.password}
        onChange={handleChange('password')}
        error={fieldErrors.password}
        hint={isEdit ? 'Leave blank to keep the current password.' : undefined}
      />

      <Checkbox label="Active account" checked={values.is_active} onChange={handleChange('is_active')} />

      <div>
        <Button type="submit" loading={submitting}>
          {isEdit ? 'Save changes' : 'Create account'}
        </Button>
      </div>
    </form>
  );
}
