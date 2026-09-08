import axios from 'axios';
import { tokenStorage } from './tokenStorage';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach the current access token to every outgoing request.
apiClient.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A separate, interceptor-free client for the refresh call itself, so a
// failed refresh can never recursively trigger another refresh attempt.
const refreshClient = axios.create({ baseURL: API_BASE_URL });

let refreshPromise = null;

/**
 * Ensures only one refresh request is ever in flight at a time. If three
 * requests 401 in parallel (e.g. a page firing several list calls at once),
 * they all await the same promise instead of racing three separate
 * refreshes against the rotate-and-blacklist refresh endpoint, where the
 * second refresh would fail because the first already rotated the token.
 */
function refreshAccessToken() {
  if (!refreshPromise) {
    const refresh = tokenStorage.getRefresh();
    if (!refresh) {
      return Promise.reject(new Error('No refresh token available.'));
    }
    refreshPromise = refreshClient
      .post('/auth/token/refresh/', { refresh })
      .then(({ data }) => {
        tokenStorage.setSession({ access: data.access, refresh: data.refresh });
        return data.access;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

// Track requests that have already retried once, so a 401 immediately after
// a refresh (e.g. the refresh token itself is invalid/expired) fails cleanly
// instead of looping.
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    const isAuthEndpoint = config?.url?.includes('/auth/login') || config?.url?.includes('/auth/token/refresh');

    if (response?.status === 401 && !config._retry && !isAuthEndpoint && tokenStorage.getRefresh()) {
      config._retry = true;
      try {
        const newAccess = await refreshAccessToken();
        config.headers.Authorization = `Bearer ${newAccess}`;
        return apiClient(config);
      } catch (refreshError) {
        tokenStorage.clear();
        // A full reload sends the user back through the router's guards
        // with a clean slate instead of leaving stale UI state around.
        if (typeof window !== 'undefined') {
          window.location.assign('/login');
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
