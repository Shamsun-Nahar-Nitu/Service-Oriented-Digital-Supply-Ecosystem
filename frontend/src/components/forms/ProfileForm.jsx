import { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Button } from '../ui/Button';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { getErrorMessage, getFieldErrors } from '../../utils/errors';

/** Editable subset of the profile — email/role/is_active are read-only server-side. */
export function ProfileForm() {
  const { user, updateProfile } = useAuth();
  const toast = useToast();
  const [values, setValues] = useState({
    first_name: user.first_name ?? '',
    last_name: user.last_name ?? '',
    phone_number: user.phone_number ?? '',
    address: user.address ?? '',
  });
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);

  function handleChange(field) {
    return (event) => setValues((current) => ({ ...current, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setFieldErrors({});
    try {
      await updateProfile(values);
      toast.success('Profile updated.');
    } catch (error) {
      setFieldErrors(getFieldErrors(error));
      toast.error(getErrorMessage(error, 'Could not update your profile.'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <Input label="Email address" value={user.email} disabled hint="Contact support to change your email." />

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

      <Textarea
        label="Address"
        rows={3}
        value={values.address}
        onChange={handleChange('address')}
        error={fieldErrors.address}
        hint="Used as your default shipping address at checkout."
      />

      <Button type="submit" loading={loading} className="self-start">
        Save changes
      </Button>
    </form>
  );
}
