import { apiClient } from './client';

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
};
