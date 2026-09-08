import { apiClient } from './client';

/**
 * Endpoints under /auth/ (apps/users). Registration is intentionally
 * restricted server-side to CUSTOMER/VENDOR roles — see
 * apps/users/serializers.py::RegisterSerializer.
 */
export const authApi = {
  register(payload) {
    return apiClient.post('/auth/register/', payload).then((r) => r.data);
  },
  login(payload) {
    return apiClient.post('/auth/login/', payload).then((r) => r.data);
  },
  fetchProfile() {
    return apiClient.get('/auth/me/').then((r) => r.data);
  },
  updateProfile(payload) {
    return apiClient.patch('/auth/me/', payload).then((r) => r.data);
  },
  changePassword(payload) {
    return apiClient.post('/auth/change-password/', payload).then((r) => r.data);
  },
};

/** Admin-only user management (/auth/users/). */
export const adminUsersApi = {
  list(params) {
    return apiClient.get('/auth/users/', { params }).then((r) => r.data);
  },
  retrieve(id) {
    return apiClient.get(`/auth/users/${id}/`).then((r) => r.data);
  },
  create(payload) {
    return apiClient.post('/auth/users/', payload).then((r) => r.data);
  },
  update(id, payload) {
    return apiClient.patch(`/auth/users/${id}/`, payload).then((r) => r.data);
  },
  remove(id) {
    return apiClient.delete(`/auth/users/${id}/`).then((r) => r.data);
  },
};
