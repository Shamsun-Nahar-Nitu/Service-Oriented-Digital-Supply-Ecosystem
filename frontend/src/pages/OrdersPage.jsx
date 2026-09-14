import { useSearchParams } from 'react-router-dom';
import { PackageOpen } from 'lucide-react';
import { transactionsApi } from '../api/transactions';
import { useFetch } from '../hooks/useFetch';
import { OrderCard } from '../components/orders/OrderCard';
import { Pagination } from '../components/ui/Pagination';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { Select } from '../components/ui/Select';
import { PageHeader } from '../components/ui/PageHeader';
import { ORDER_STATUS_LABELS } from '../utils/constants';

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  ...Object.entries(ORDER_STATUS_LABELS).map(([value, label]) => ({ value, label })),
];

/**
 * Scoped entirely server-side: /transactions/ already returns only the
 * signed-in user's own orders for customers (see
 * apps/transactions/views.py::TransactionViewSet.get_queryset), so no
 * client-side filtering by user is needed here.
 */
export default function OrdersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const status = searchParams.get('status') ?? '';
  const page = Number(searchParams.get('page') ?? '1');

  const { data, loading, error, refetch } = useFetch(
    () => transactionsApi.list({ status: status || undefined, ordering: '-created_date', page }),
    [status, page]
  );

  function handleStatusChange(value) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set('status', value);
    else next.delete('status');
    next.delete('page');
    setSearchParams(next);
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6">
      <PageHeader
        title="My orders"
        action={
          <Select
            aria-label="Filter by status"
            options={STATUS_OPTIONS}
            value={status}
            onChange={(event) => handleStatusChange(event.target.value)}
            className="w-48"
          />
        }
      />

      {error ? (
        <ErrorState error={error} onRetry={refetch} />
      ) : !loading && data?.results.length === 0 ? (
        <EmptyState
          icon={PackageOpen}
          title={status ? `No ${ORDER_STATUS_LABELS[status].toLowerCase()} orders` : 'No orders yet'}
          description="Once you place an order, it will show up here."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {loading
            ? Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="h-24 animate-pulse rounded-xl bg-ink-100" />
              ))
            : data.results.map((transaction) => (
                <OrderCard key={transaction.id} transaction={transaction} />
              ))}
        </div>
      )}

      <Pagination pagination={data} onPageChange={(next) => setSearchParams({ ...(status && { status }), page: next })} className="mt-6" />
    </div>
  );
}
