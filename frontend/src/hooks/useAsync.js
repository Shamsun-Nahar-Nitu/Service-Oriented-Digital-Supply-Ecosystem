import { useCallback, useState } from 'react';

/**
 * For user-triggered mutations (submit a form, click "restock", place an
 * order) rather than data loaded on mount. Exposes `run` to fire the action
 * and tracks loading/error state so a submit button can disable itself and
 * a form can surface a failure inline.
 */
export function useAsync() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = useCallback(async (action) => {
    setLoading(true);
    setError(null);
    try {
      const result = await action();
      setLoading(false);
      return result;
    } catch (err) {
      setError(err);
      setLoading(false);
      throw err;
    }
  }, []);

  return { run, loading, error, setError };
}
