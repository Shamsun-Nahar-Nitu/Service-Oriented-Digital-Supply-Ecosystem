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
import { RevenueChart } from '../../components/finance/RevenueChart';
import { StatusBreakdown } from '../../components/finance/StatusBreakdown';
import { formatCurrency, formatDate } from '../../utils/format';
import { getErrorMessage } from '../../utils/errors';

/** The signed-in vendor's own sales, commission and payable summary —
 * scoped server-side to request.user (apps.finance.views.VendorDashboardView),
 * so there's no vendor selector here: it's always "me". */
export default function VendorDashboardPage() {
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const period = searchParams.get('period') ?? DEFAULT_PERIOD;

  const { data, loading, error, refetch } = useFetch(
    () => financeApi.vendorDashboard({ period }),
    [period]
  );
  const { run: runDownload, loading: downloading } = useAsync();

  function handlePeriodChange(value) {
    setSearchParams(value === DEFAULT_PERIOD ? {} : { period: value });
  }

  async function handleDownload() {
    try {
      await runDownload(() => financeApi.downloadVendorReport({ period }));
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
        description="Your sales, payout and top performers."
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
        <KpiCard label="Gross sales" value={loading ? '—' : formatCurrency(kpis?.gross_sales)} />
        <KpiCard label="Commission paid" value={loading ? '—' : formatCurrency(kpis?.commission_paid)} hint="1% platform fee" />
        <KpiCard label="Net payable" value={loading ? '—' : formatCurrency(kpis?.net_payable)} />
        <KpiCard label="Paid orders" value={loading ? '—' : kpis?.paid_orders} />
        <KpiCard label="Active products" value={loading ? '—' : kpis?.active_products} />
        <KpiCard label="Total products" value={loading ? '—' : kpis?.total_products} />
      </KpiGrid>

      <Card className="mt-6 p-5">
        <h2 className="mb-3 text-sm font-semibold text-ink-800">Sales over time</h2>
        <RevenueChart data={data?.sales_series} valueKey="sales" />
      </Card>

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
            emptyTitle="No sales in this period"
          />
        </Card>

        <Card className="p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Top customers</h2>
          <DataTable
            columns={[
              { key: 'customer', header: 'Customer', render: (row) => row.transaction__user__email },
              { key: 'units', header: 'Units', render: (row) => row.units },
              { key: 'spend', header: 'Spend', render: (row) => formatCurrency(row.spend) },
            ]}
            rows={data?.top_customers ?? []}
            loading={loading}
            getRowKey={(row) => row.transaction__user_id}
            emptyTitle="No customers yet in this period"
          />
        </Card>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="p-5 lg:col-span-1">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Orders by status</h2>
          <StatusBreakdown data={data?.orders_by_status} />
        </Card>

        <Card className="p-5 lg:col-span-2">
          <h2 className="mb-3 text-sm font-semibold text-ink-800">Recent orders</h2>
          {!data?.recent_orders || data.recent_orders.length === 0 ? (
            <p className="py-6 text-center text-sm text-ink-500">No recent orders.</p>
          ) : (
            <ul className="divide-y divide-ink-100">
              {data.recent_orders.map((order) => (
                <li key={order.id} className="flex items-center justify-between gap-3 py-2.5 text-sm">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-ink-900">
                      {order.customer_name || order.customer_email}
                    </p>
                    <p className="truncate text-xs text-ink-500">
                      {order.items.map((item) => `${item.product} ×${item.quantity}`).join(', ')}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    <span className="text-xs text-ink-500">{formatDate(order.created_date)}</span>
                    <StatusBadge status={order.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}