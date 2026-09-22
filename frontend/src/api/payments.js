import { apiClient } from './client';
import { triggerBlobDownload } from '../utils/downloadBlob';

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
  retry(id) {
    return apiClient.post(`/payments/${id}/retry/`).then((r) => r.data);
  },
  markCodCollected(id) {
    return apiClient.post(`/payments/${id}/mark_cod_collected/`).then((r) => r.data);
  },
  async downloadReceipt(id, orderReference) {
    const { data } = await apiClient.get(`/payments/${id}/receipt/`, { responseType: 'blob' });
    triggerBlobDownload(data, `receipt-${orderReference || id}.pdf`);
  },
};