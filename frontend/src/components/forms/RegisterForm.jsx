import { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage, getFieldErrors } from '../../utils/errors';

const ROLE_OPTIONS = [
  { value: 'CUSTOMER', label: 'Customer — I want to shop' },
  { value: 'VENDOR', label: 'Vendor — I want to sell products' },
];

const EMPTY_VALUES = {
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  address: '',
  role: 'CUSTOMER',
  password: '',
  confirm_password: '',
};

/**
 * Self-registration is only open to CUSTOMER/VENDOR roles server-side
 * (apps/users/serializers.py::RegisterSerializer.SELF_REGISTERABLE_ROLES) —
 * admin/manager accounts are provisioned separately, so this form only ever
 * offers the two roles the API will actually accept.
 */
export function RegisterForm({ onSuccess }) {
  const { register } = useAuth();
  const [values, setValues] = useState(EMPTY_VALUES);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleChange(field) {
    return (event) => setValues((current) => ({ ...current, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setFormError(null);
    setFieldErrors({});
    try {
      await register(values);
      onSuccess?.(values.email);
    } catch (error) {
      setFieldErrors(getFieldErrors(error));
      setFormError(getErrorMessage(error, 'Could not create your account.'));
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

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          label="First name"
          required
          autoComplete="given-name"
          value={values.first_name}
          onChange={handleChange('first_name')}
          error={fieldErrors.first_name}
        />
        <Input
          label="Last name"
          required
          autoComplete="family-name"
          value={values.last_name}
          onChange={handleChange('last_name')}
          error={fieldErrors.last_name}
        />
      </div>

      <Input
        label="Email address"
        type="email"
        required
        autoComplete="email"
        value={values.email}
        onChange={handleChange('email')}
        error={fieldErrors.email}
      />

      <Input
        label="Phone number"
        type="tel"
        autoComplete="tel"
        value={values.phone_number}
        onChange={handleChange('phone_number')}
        error={fieldErrors.phone_number}
        hint="Optional, but useful for delivery updates."
      />

      <Textarea
        label="Address"
        rows={2}
        value={values.address}
        onChange={handleChange('address')}
        error={fieldErrors.address}
        hint="Optional — you can also add this later at checkout."
      />

      <Select
        label="Account type"
        required
        options={ROLE_OPTIONS}
        value={values.role}
        onChange={handleChange('role')}
        error={fieldErrors.role}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          label="Password"
          type="password"
          required
          autoComplete="new-password"
          value={values.password}
          onChange={handleChange('password')}
          error={fieldErrors.password}
        />
        <Input
          label="Confirm password"
          type="password"
          required
          autoComplete="new-password"
          value={values.confirm_password}
          onChange={handleChange('confirm_password')}
          error={fieldErrors.confirm_password}
        />
      </div>

      <Button type="submit" fullWidth loading={loading} className="mt-2">
        Create account
      </Button>
    </form>
  );
}
