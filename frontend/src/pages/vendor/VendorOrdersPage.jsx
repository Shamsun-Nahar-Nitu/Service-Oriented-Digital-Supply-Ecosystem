import { useSearchParams } from 'react-router-dom';
import { PackageOpen } from 'lucide-react';
import { transactionsApi } from '../../api/transactions';
import { useFetch } from '../../hooks/useFetch';
import { OrderCard } from '../../components/orders/OrderCard';
import { Pagination } from '../../components/ui/Pagination';
import { EmptyState } from '../../components/ui/EmptyState';
import { ErrorState } from '../../components/ui/ErrorState';
import { PageHeader } from '../../components/ui/PageHeader';

/**
 * Read-only by design: vendors can see any order containing one of their
 * products (apps/transactions/views.py filters by items__product__vendor),
 * but only admin/manager can move an order through its status lifecycle.
 */
export default function VendorOrdersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get('page') ?? '1');

  const { data, loading, error, refetch } = useFetch(
    () => transactionsApi.list({ ordering: '-created_date', page }),
    [page]
  );

  return (
    <div>
      <PageHeader
        title="Orders with my products"
        description="Read-only — order status is managed by ShopNest staff."
      />

      {error ? (
        <ErrorState error={error} onRetry={refetch} />
      ) : !loading && data?.results.length === 0 ? (
        <EmptyState icon={PackageOpen} title="No orders yet" description="Orders containing your products will appear here." />
      ) : (
        <div className="flex flex-col gap-3">
          {loading
            ? Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="h-24 animate-pulse rounded-xl bg-ink-100" />
              ))
            : data.results.map((transaction) => <OrderCard key={transaction.id} transaction={transaction} />)}
        </div>
      )}

      <Pagination pagination={data} onPageChange={(next) => setSearchParams({ page: next })} className="mt-4" />
    </div>
  );
}
