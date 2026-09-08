/**
 * Every error response from the API shares one envelope (see
 * apps/core/exceptions.py::custom_exception_handler):
 *
 *   { "success": false, "status_code": 400, "errors": { field: [msg, ...] } }
 *
 * `errors` can be a field->messages map (validation errors), or a plain
 * { detail: "..." } object (auth/permission/not-found/throttle errors).
 * These helpers normalize both shapes for display.
 */

/** Flattens the error envelope into a single human-readable string. */
export function getErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  const data = error?.response?.data;
  if (!data) {
    if (error?.message === 'Network Error') {
      return 'Cannot reach the server. Check your connection and try again.';
    }
    return fallback;
  }

  const errors = data.errors ?? data;
  if (typeof errors === 'string') return errors;
  if (Array.isArray(errors)) return errors[0] ?? fallback;
  if (errors?.detail) return errors.detail;

  if (errors && typeof errors === 'object') {
    const firstKey = Object.keys(errors)[0];
    if (firstKey) {
      const value = errors[firstKey];
      const message = Array.isArray(value) ? value[0] : value;
      // Prefix with the field name for non-obvious fields so the person
      // knows what to fix, e.g. "confirm_password: Passwords do not match."
      if (firstKey !== 'non_field_errors' && firstKey !== 'detail') {
        return `${humanizeField(firstKey)}: ${message}`;
      }
      return message;
    }
  }

  return fallback;
}

/** Maps API field errors onto a flat { field: message } object for form inputs. */
export function getFieldErrors(error) {
  const data = error?.response?.data;
  const errors = data?.errors ?? data;
  if (!errors || typeof errors !== 'object') return {};

  const fieldErrors = {};
  Object.entries(errors).forEach(([field, value]) => {
    if (field === 'detail') return;
    fieldErrors[field] = Array.isArray(value) ? value[0] : String(value);
  });
  return fieldErrors;
}

/**
 * Every read endpoint in this API requires authentication (see
 * DEFAULT_PERMISSION_CLASSES in config/settings/base.py) — there is no
 * anonymous browsing. A 401/403 here almost always means "log in to see
 * this", not "something broke", so callers should route it to a sign-in
 * prompt rather than a generic error state.
 */
export function isAuthError(error) {
  const status = error?.response?.status;
  return status === 401 || status === 403;
}

function humanizeField(field) {
  return field
    .replace(/_/g, ' ')
    .replace(/^\w/, (char) => char.toUpperCase());
}
