import { apiClient } from './client';

/** /transactions/ — orders. Checkout is a custom action, not a plain POST. */
export const transactionsApi = {
  list(params) {
    return apiClient.get('/transactions/', { params }).then((r) => r.data);
  },
  retrieve(id) {
    return apiClient.get(`/transactions/${id}/`).then((r) => r.data);
  },
  checkout(payload) {
    return apiClient.post('/transactions/checkout/', payload).then((r) => r.data);
  },
  updateStatus(id, status) {
    return apiClient.patch(`/transactions/${id}/update_status/`, { status }).then((r) => r.data);
  },
  cancel(id) {
    return apiClient.post(`/transactions/${id}/cancel/`).then((r) => r.data);
  },
};
