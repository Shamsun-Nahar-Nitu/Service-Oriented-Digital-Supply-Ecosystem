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
import { StatusBadge } from '../../components/ui/StatusBadge';
import { ErrorState } from '../../components/ui/ErrorState';
import { KpiCard, KpiGrid } from '../../components/finance/KpiCard';
import { PeriodSelect, DEFAULT_PERIOD } from '../../components/finance/PeriodSelect';
import { StatusBreakdown } from '../../components/finance/StatusBreakdown';
import { formatCurrency, formatDate, pluralize } from '../../utils/format';
import { getErrorMessage } from '../../utils/errors';

/**
 * Vendor and customer monitoring — ADMIN and MANAGER (see IsAdminOrManager
 * on apps.finance.views.ManagerDashboardView). Deliberately no revenue KPI
 * here — that's the admin-only /admin/dashboard; this page is about
 * operational oversight: who's performing, who needs attention, what's
 * running low.
 */
export default function ManagerDashboardPage() {
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const period = searchParams.get('period') ?? DEFAULT_PERIOD;

  const { data, loading, error, refetch } = useFetch(
    () => financeApi.managerDashboard({ period }),
    [period]
  );
  const { run: runDownload, loading: downloading } = useAsync();

  function handlePeriodChange(value) {
    setSearchParams(value === DEFAULT_PERIOD ? {} : { period: value });
  }

  async function handleDownload() {
    try {
      await runDownload(() => financeApi.downloadManagerReport({ period }));
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not generate the report.'));
    }
  }

  if (error) {
    return (
      <div>
        <PageHeader title="Monitoring" />
        <ErrorState error={error} onRetry={refetch} />
      </div>
    );
  }

  const kpis = data?.kpis;

  return (
    <div>
      <PageHeader
        title="Monitoring"
        description="Vendor performance, customer activity and things that need attention."
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
        <KpiCard label="Total customers" value={loading ? '—' : kpis?.total_customers} hint={loading ? undefined : `+${kpis?.new_customers} new`} />
        <KpiCard label="Total vendors" value={loading ? '—' : kpis?.total_vendors} />
        <KpiCard label="Needs attention" value={loading ? '—' : kpis?.orders_needing_attention} hint="Pending 3+ days" />
        <KpiCard label="Low stock products" value={loading ? '—' : kpis?.low_stock_products} />
      </KpiGrid>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Vendor performance</h2>
          <DataTable
            columns={[
              { key: 'vendor', header: 'Vendor', render: (row) => row.vendor__email },
              { key: 'sales', header: 'Sales', render: (row) => formatCurrency(row.sales) },
              { key: 'payable', header: 'Payable', render: (row) => formatCurrency(row.payable) },
              { key: 'products', header: 'Products', render: (row) => row.product_count },
            ]}
            rows={data?.vendor_performance ?? []}
            loading={loading}
            getRowKey={(row) => row.vendor_id}
            emptyTitle="No vendor sales in this period"
          />
        </Card>

        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Top customers</h2>
          <DataTable
            columns={[
              { key: 'customer', header: 'Customer', render: (row) => row.user__email },
              { key: 'spend', header: 'Total spend', render: (row) => formatCurrency(row.total_spend) },
              { key: 'orders', header: 'Orders', render: (row) => pluralize(row.orders, 'order') },
            ]}
            rows={data?.customer_activity ?? []}
            loading={loading}
            getRowKey={(row) => row.user_id}
            emptyTitle="No customer activity in this period"
          />
        </Card>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Orders by status</h2>
          <StatusBreakdown data={data?.orders_by_status} />
        </Card>

        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Low stock alerts</h2>
          <DataTable
            columns={[
              { key: 'product', header: 'Product', render: (row) => row.product__product_name },
              { key: 'vendor', header: 'Vendor', render: (row) => row.product__vendor__email },
              { key: 'stock', header: 'In stock', render: (row) => row.quantity_in_stock },
              { key: 'reorder', header: 'Reorder at', render: (row) => row.reorder_level },
            ]}
            rows={data?.low_stock_alerts ?? []}
            loading={loading}
            getRowKey={(row) => row.product__sku}
            emptyTitle="Nothing low on stock"
          />
        </Card>
      </div>

      <Card className="mt-6 p-5">
        <h2 className="mb-3 text-sm font-semibold text-ink-800">Orders needing attention</h2>
        <p className="mb-3 text-xs text-ink-500">Pending or confirmed for more than 3 days.</p>
        <DataTable
          columns={[
            { key: 'order', header: 'Order', render: (row) => `#${String(row.transaction_number).slice(0, 8)}` },
            { key: 'customer', header: 'Customer', render: (row) => row.user__email },
            { key: 'total', header: 'Total', render: (row) => formatCurrency(row.total_amount) },
            { key: 'status', header: 'Status', render: (row) => <StatusBadge status={row.status} /> },
            { key: 'placed', header: 'Placed', render: (row) => formatDate(row.created_date) },
          ]}
          rows={data?.pending_attention ?? []}
          loading={loading}
          getRowKey={(row) => row.id}
          emptyTitle="Nothing waiting on attention"
        />
      </Card>
    </div>
  );
}