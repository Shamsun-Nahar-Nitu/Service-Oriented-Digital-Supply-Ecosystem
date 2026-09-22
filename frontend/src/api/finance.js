import { apiClient } from './client';
import { triggerBlobDownload } from '../utils/downloadBlob';

/**
 * /finance/ — commission ledger dashboards and their PDF reports
 * (apps/finance/views.py). All three dashboard endpoints and their PDF
 * counterparts take the same three query params, so `params` is passed
 * straight through rather than having each call spell out its shape:
 *   - period: '7d' | '30d' | '90d' | '12m' | 'this_month' | 'last_month' | 'all'
 *   - start / end: explicit 'YYYY-MM-DD', override period when present
 *   - granularity: 'day' | 'month' for the revenue/sales time series
 */
export const financeApi = {
  adminDashboard(params) {
    return apiClient.get('/finance/dashboard/admin/', { params }).then((r) => r.data);
  },
  managerDashboard(params) {
    return apiClient.get('/finance/dashboard/manager/', { params }).then((r) => r.data);
  },
  vendorDashboard(params) {
    return apiClient.get('/finance/dashboard/vendor/', { params }).then((r) => r.data);
  },

  async downloadAdminReport(params) {
    const { data } = await apiClient.get('/finance/reports/admin/', { params, responseType: 'blob' });
    triggerBlobDownload(data, 'admin-report.pdf');
  },
  async downloadManagerReport(params) {
    const { data } = await apiClient.get('/finance/reports/manager/', { params, responseType: 'blob' });
    triggerBlobDownload(data, 'manager-report.pdf');
  },
  async downloadVendorReport(params) {
    const { data } = await apiClient.get('/finance/reports/vendor/', { params, responseType: 'blob' });
    triggerBlobDownload(data, 'vendor-report.pdf');
  },
};