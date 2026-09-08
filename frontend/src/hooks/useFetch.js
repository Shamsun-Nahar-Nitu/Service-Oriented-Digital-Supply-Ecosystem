import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Runs an async fetcher on mount and whenever `deps` changes, tracking
 * loading/error/data state so pages don't each hand-roll the same
 * try/catch/isMounted boilerplate. Stale responses (a slow request that
 * resolves after a newer one has already started) are dropped instead of
 * clobbering fresher data — important for search-as-you-type filters.
 *
 * Pass `skip: true` to opt out of the automatic fetch (e.g. while a
 * dependent value like an id is still undefined).
 */
export function useFetch(fetcher, deps = [], { skip = false } = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(!skip);
  const [error, setError] = useState(null);
  const requestId = useRef(0);

  const run = useCallback(() => {
    const id = (requestId.current += 1);
    setLoading(true);
    setError(null);
    return fetcher()
      .then((result) => {
        if (id === requestId.current) {
          setData(result);
          setLoading(false);
        }
        return result;
      })
      .catch((err) => {
        if (id === requestId.current) {
          setError(err);
          setLoading(false);
        }
        throw err;
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    if (skip) return undefined;
    run().catch(() => {
      // Error is already captured in state; swallow so this doesn't
      // surface as an unhandled promise rejection in the console.
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skip, ...deps]);

  return { data, loading, error, refetch: run, setData };
}
