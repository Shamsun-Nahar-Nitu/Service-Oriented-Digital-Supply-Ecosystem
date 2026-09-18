import { useSearchParams } from 'react-router-dom';
import { Download } from 'lucide-react';
import { financeApi } from '../../api/finance';
import { useFetch } from '../../hooks/useFetch';
import { useAsync } from '../../hooks/useAsync';
import { useToast } from '../../context/ToastContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { DataTable } from '../../components/ui/DataTable';
import { ErrorState } from '../../components/ui/ErrorState';
import { KpiCard, KpiGrid } from '../../components/finance/KpiCard';
import { PeriodSelect, DEFAULT_PERIOD } from '../../components/finance/PeriodSelect';
import { RevenueChart } from '../../components/finance/RevenueChart';
import { StatusBreakdown } from '../../components/finance/StatusBreakdown';
import { formatCurrency, pluralize } from '../../utils/format';
import { getErrorMessage } from '../../utils/errors';

/**
 * Platform-wide revenue and commission KPIs — ADMIN only (see the
 * IsAdmin permission on apps.finance.views.AdminDashboardView). Managers
 * get the narrower vendor/customer monitoring view at /admin/monitoring
 * instead; this page is specifically the money view.
 */
export default function AdminDashboardPage() {
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const period = searchParams.get('period') ?? DEFAULT_PERIOD;

  const { data, loading, error, refetch } = useFetch(
    () => financeApi.adminDashboard({ period }),
    [period]
  );
  const { run: runDownload, loading: downloading } = useAsync();

  function handlePeriodChange(value) {
    setSearchParams(value === DEFAULT_PERIOD ? {} : { period: value });
  }

  async function handleDownload() {
    try {
      await runDownload(() => financeApi.downloadAdminReport({ period }));
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not generate the report.'));
    }
  }

  if (error) {
    return (
      <div>
        <PageHeader title="Dashboard" />
        <ErrorState error={error} onRetry={refetch} />
      </div>
    );
  }

  const kpis = data?.kpis;

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Platform-wide revenue, commission and growth."
        action={
          <>
            <PeriodSelect value={period} onChange={handlePeriodChange} />
            <Button variant="outline" size="md" onClick={handleDownload} loading={downloading}>
              <Download className="h-4 w-4" aria-hidden="true" />
              PDF
            </Button>
          </>
        }
      />

      <KpiGrid>
        <KpiCard label="Gross revenue" value={loading ? '—' : formatCurrency(kpis?.gross_revenue)} />
        <KpiCard label="Platform revenue" value={loading ? '—' : formatCurrency(kpis?.platform_revenue)} hint="1% customer + 1% vendor" />
        <KpiCard label="Vendor payout" value={loading ? '—' : formatCurrency(kpis?.vendor_payout)} />
        <KpiCard label="Avg. order value" value={loading ? '—' : formatCurrency(kpis?.average_order_value)} />
        <KpiCard label="Paid orders" value={loading ? '—' : kpis?.paid_orders} />
        <KpiCard label="Orders placed" value={loading ? '—' : kpis?.orders_placed} />
        <KpiCard label="Total customers" value={loading ? '—' : kpis?.total_customers} hint={loading ? undefined : `+${kpis?.new_customers} new`} />
        <KpiCard label="Total vendors" value={loading ? '—' : kpis?.total_vendors} hint={loading ? undefined : `+${kpis?.new_vendors} new`} />
      </KpiGrid>

      <Card className="mt-6 p-5">
        <h2 className="mb-3 text-sm font-semibold text-ink-800">Revenue over time</h2>
        <RevenueChart data={data?.revenue_series} valueKey="revenue" />
      </Card>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Orders by status</h2>
          <StatusBreakdown data={data?.orders_by_status} />
        </Card>

        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Top vendors</h2>
          <DataTable
            columns={[
              { key: 'vendor', header: 'Vendor', render: (row) => row.vendor__email },
              { key: 'sales', header: 'Sales', render: (row) => formatCurrency(row.sales) },
              { key: 'commission', header: 'Commission', render: (row) => formatCurrency(row.commission) },
              { key: 'orders', header: 'Orders', render: (row) => pluralize(row.orders, 'order') },
            ]}
            rows={data?.top_vendors ?? []}
            loading={loading}
            getRowKey={(row) => row.vendor_id}
            emptyTitle="No vendor sales in this period"
          />
        </Card>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Top products</h2>
          <DataTable
            columns={[
              { key: 'product', header: 'Product', render: (row) => row.product__product_name },
              { key: 'units', header: 'Units sold', render: (row) => row.units_sold },
              { key: 'revenue', header: 'Revenue', render: (row) => formatCurrency(row.revenue) },
            ]}
            rows={data?.top_products ?? []}
            loading={loading}
            getRowKey={(row) => row.product_id}
            emptyTitle="No product sales in this period"
          />
        </Card>

        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Top categories</h2>
          <DataTable
            columns={[
              { key: 'category', header: 'Category', render: (row) => row.product__category__name ?? 'Uncategorized' },
              { key: 'units', header: 'Units sold', render: (row) => row.units_sold },
              { key: 'revenue', header: 'Revenue', render: (row) => formatCurrency(row.revenue) },
            ]}
            rows={data?.top_categories ?? []}
            loading={loading}
            getRowKey={(row) => row.product__category_id ?? 'none'}
            emptyTitle="No category sales in this period"
          />
        </Card>
      </div>
    </div>
  );
}