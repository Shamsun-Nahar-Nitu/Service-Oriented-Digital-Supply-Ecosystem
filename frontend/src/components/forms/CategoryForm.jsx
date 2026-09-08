import { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Select } from '../ui/Select';
import { Checkbox } from '../ui/Checkbox';
import { Button } from '../ui/Button';
import { getErrorMessage, getFieldErrors } from '../../utils/errors';

function toFormValues(category) {
  return {
    name: category?.name ?? '',
    code: category?.code ?? '',
    description: category?.description ?? '',
    parent: category?.parent ? String(category.parent) : '',
    is_active: category?.is_active ?? true,
  };
}

/** Admin/manager-only create/edit form for a category or subcategory. */
export function CategoryForm({ category, categories, onSubmit }) {
  const isEdit = Boolean(category);
  const [values, setValues] = useState(() => toFormValues(category));
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // A category can't be its own parent.
  const parentOptions = categories.filter((option) => option.id !== category?.id);

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

    try {
      await onSubmit({
        ...values,
        parent: values.parent ? Number(values.parent) : null,
      });
    } catch (error) {
      setFieldErrors(getFieldErrors(error));
      setFormError(getErrorMessage(error, 'Could not save this category.'));
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
        label="Name"
        required
        value={values.name}
        onChange={handleChange('name')}
        error={fieldErrors.name}
      />
      <Input
        label="Code"
        required
        value={values.code}
        onChange={handleChange('code')}
        error={fieldErrors.code}
        hint="Short unique identifier, e.g. ELEC."
      />
      <Textarea
        label="Description"
        rows={3}
        value={values.description}
        onChange={handleChange('description')}
        error={fieldErrors.description}
      />
      <Select
        label="Parent category"
        placeholder="None — top-level category"
        options={parentOptions.map((option) => ({ value: String(option.id), label: option.name }))}
        value={values.parent}
        onChange={handleChange('parent')}
        error={fieldErrors.parent}
      />
      <Checkbox label="Active" checked={values.is_active} onChange={handleChange('is_active')} />
      <div>
        <Button type="submit" loading={submitting}>
          {isEdit ? 'Save changes' : 'Create category'}
        </Button>
      </div>
    </form>
  );
}
