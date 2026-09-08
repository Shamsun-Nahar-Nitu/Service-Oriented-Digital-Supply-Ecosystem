import { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Select } from '../ui/Select';
import { Checkbox } from '../ui/Checkbox';
import { Button } from '../ui/Button';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage, getFieldErrors } from '../../utils/errors';
import { PRODUCT_ISSUE_LABELS } from '../../utils/constants';

const ISSUE_OPTIONS = Object.entries(PRODUCT_ISSUE_LABELS).map(([value, label]) => ({ value, label }));

function toFormValues(product) {
  return {
    product_name: product?.product_name ?? '',
    sku: product?.sku ?? '',
    description: product?.description ?? '',
    brand: product?.brand ?? '',
    category: product?.category ? String(product.category) : '',
    vendor: product?.vendor ? String(product.vendor) : '',
    issues: product?.issues ?? 'NONE',
    expire_date: product?.expire_date ?? '',
    mrp: product?.mrp ?? '',
    discount_percentage: product?.discount_percentage ?? '0',
    is_active: product?.is_active ?? true,
  };
}

/**
 * Shared create/edit form for both the vendor dashboard and the admin
 * console. Which fields are editable differs by role, mirroring the
 * backend: vendors never see a `vendor` field — the API silently forces
 * vendor = request.user for vendor-authored requests regardless of payload
 * (apps/products/serializers.py::ProductSerializer.validate) — while
 * admins/managers must supply one, since there's no request.user vendor to
 * fall back on. Managers additionally have no API access to browse the
 * vendor list (/auth/users/ is admin-only), so they get a plain ID field
 * instead of a picker — a real constraint of this backend, not an
 * oversight, and it's better to say so than to fake a dropdown.
 */
export function ProductForm({ product, categories, categoriesLoading, vendorOptions, onSubmit }) {
  const { isVendor, isAdmin } = useAuth();
  const isEdit = Boolean(product);
  const [values, setValues] = useState(() => toFormValues(product));
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

    const payload = {
      product_name: values.product_name,
      sku: values.sku,
      description: values.description,
      brand: values.brand,
      category: values.category ? Number(values.category) : null,
      issues: values.issues,
      expire_date: values.expire_date || null,
      mrp: values.mrp,
      discount_percentage: values.discount_percentage,
      is_active: values.is_active,
    };
    if (!isVendor && values.vendor) {
      payload.vendor = Number(values.vendor);
    }

    try {
      await onSubmit(payload);
    } catch (error) {
      setFieldErrors(getFieldErrors(error));
      setFormError(getErrorMessage(error, 'Could not save this product.'));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5" noValidate>
      {formError && (
        <p role="alert" className="rounded-lg bg-danger-50 px-3 py-2 text-sm text-danger-700">
          {formError}
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          label="Product name"
          required
          value={values.product_name}
          onChange={handleChange('product_name')}
          error={fieldErrors.product_name}
        />
        <Input
          label="SKU"
          required
          value={values.sku}
          onChange={handleChange('sku')}
          error={fieldErrors.sku}
          hint="Must be unique across the catalog."
        />
      </div>

      <Textarea
        label="Description"
        rows={4}
        value={values.description}
        onChange={handleChange('description')}
        error={fieldErrors.description}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input label="Brand" value={values.brand} onChange={handleChange('brand')} error={fieldErrors.brand} />
        <Select
          label="Category"
          required
          placeholder="Select a category"
          options={categories.map((category) => ({ value: String(category.id), label: category.name }))}
          value={values.category}
          onChange={handleChange('category')}
          disabled={categoriesLoading}
          error={fieldErrors.category}
        />
      </div>

      {!isVendor &&
        (isAdmin ? (
          <Select
            label="Vendor"
            required={!isEdit}
            placeholder="Select the owning vendor"
            options={vendorOptions.map((vendor) => ({
              value: String(vendor.id),
              label: vendor.full_name || vendor.email,
            }))}
            value={values.vendor}
            onChange={handleChange('vendor')}
            error={fieldErrors.vendor}
          />
        ) : (
          <Input
            label="Vendor ID"
            required={!isEdit}
            type="number"
            hint="Managers can't browse the vendor list — enter the vendor account's numeric ID directly."
            value={values.vendor}
            onChange={handleChange('vendor')}
            error={fieldErrors.vendor}
          />
        ))}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Input
          label="MRP"
          type="number"
          min="0"
          step="0.01"
          required
          value={values.mrp}
          onChange={handleChange('mrp')}
          error={fieldErrors.mrp}
        />
        <Input
          label="Discount %"
          type="number"
          min="0"
          max="100"
          step="0.01"
          value={values.discount_percentage}
          onChange={handleChange('discount_percentage')}
          error={fieldErrors.discount_percentage}
        />
        <Input
          label="Expiry date"
          type="date"
          hint="Leave blank for non-perishables."
          value={values.expire_date}
          onChange={handleChange('expire_date')}
          error={fieldErrors.expire_date}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Select
          label="Issue status"
          options={ISSUE_OPTIONS}
          value={values.issues}
          onChange={handleChange('issues')}
          error={fieldErrors.issues}
          hint="Flags this listing for review — hidden from shoppers until cleared."
        />
        <div className="flex items-end pb-2.5">
          <Checkbox
            label="Active — visible in the storefront"
            checked={values.is_active}
            onChange={handleChange('is_active')}
          />
        </div>
      </div>

      <div>
        <Button type="submit" loading={submitting}>
          {isEdit ? 'Save changes' : 'Create product'}
        </Button>
      </div>
    </form>
  );
}
