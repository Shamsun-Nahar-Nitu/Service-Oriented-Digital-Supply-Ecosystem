import { apiClient } from './client';

/**
 * /products/ supports search, ordering, and the custom filters defined in
 * apps/products/filters.py (min_price, max_price, in_stock) in addition to
 * the plain field filters (category, vendor, brand, issues, is_active).
 * `params` is passed straight through as query params, so callers can mix
 * any of those keys freely.
 */
export const productsApi = {
  list(params) {
    return apiClient.get('/products/', { params }).then((r) => r.data);
  },
  retrieve(id) {
    return apiClient.get(`/products/${id}/`).then((r) => r.data);
  },
  create(payload) {
    return apiClient.post('/products/', payload).then((r) => r.data);
  },
  update(id, payload) {
    return apiClient.patch(`/products/${id}/`, payload).then((r) => r.data);
  },
  remove(id) {
    return apiClient.delete(`/products/${id}/`).then((r) => r.data);
  },
};
