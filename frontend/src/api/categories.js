import { apiClient } from './client';

export const categoriesApi = {
  list(params) {
    return apiClient.get('/categories/', { params }).then((r) => r.data);
  },
  retrieve(id) {
    return apiClient.get(`/categories/${id}/`).then((r) => r.data);
  },
  create(payload) {
    return apiClient.post('/categories/', payload).then((r) => r.data);
  },
  update(id, payload) {
    return apiClient.patch(`/categories/${id}/`, payload).then((r) => r.data);
  },
  remove(id) {
    return apiClient.delete(`/categories/${id}/`).then((r) => r.data);
  },
};
