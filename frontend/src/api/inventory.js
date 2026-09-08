import { apiClient } from './client';

/** /inventory/ — admin/manager only (apps/inventory/views.py). */
export const inventoryApi = {
  list(params) {
    return apiClient.get('/inventory/', { params }).then((r) => r.data);
  },
  retrieve(id) {
    return apiClient.get(`/inventory/${id}/`).then((r) => r.data);
  },
  update(id, payload) {
    return apiClient.patch(`/inventory/${id}/`, payload).then((r) => r.data);
  },
  restock(id, payload) {
    return apiClient.post(`/inventory/${id}/restock/`, payload).then((r) => r.data);
  },
  movements(id) {
    return apiClient.get(`/inventory/${id}/movements/`).then((r) => r.data);
  },
};
