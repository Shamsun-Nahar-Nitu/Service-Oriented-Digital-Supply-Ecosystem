import { apiClient } from './client';

/**
 * /payments/ — there is no real payment gateway wired in on the backend;
 * `confirm` simulates the webhook a provider like Stripe would send (see
 * apps/payments/views.py::PaymentViewSet.confirm).
 */
export const paymentsApi = {
  list(params) {
    return apiClient.get('/payments/', { params }).then((r) => r.data);
  },
  retrieve(id) {
    return apiClient.get(`/payments/${id}/`).then((r) => r.data);
  },
  initiate(payload) {
    return apiClient.post('/payments/', payload).then((r) => r.data);
  },
  confirm(id, payload) {
    return apiClient.post(`/payments/${id}/confirm/`, payload).then((r) => r.data);
  },
};
