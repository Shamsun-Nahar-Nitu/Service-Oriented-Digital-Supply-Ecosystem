import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Eye } from 'lucide-react';
import { transactionsApi } from '../../api/transactions';
import { useFetch } from '../../hooks/useFetch';
import { useAsync } from '../../hooks/useAsync';
import { useToast } from '../../context/ToastContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { DataTable } from '../../components/ui/DataTable';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Select } from '../../components/ui/Select';
import { Button } from '../../components/ui/Button';
import { Pagination } from '../../components/ui/Pagination';
import { formatCurrency, formatDate, pluralize } from '../../utils/format';
import { getErrorMessage } from '../../utils/errors';
import { ORDER_STATUS_LABELS } from '../../utils/constants';

const STATUS_FILTER_OPTIONS = [
  { value: '', label: 'All statuses' },
  ...Object.entries(ORDER_STATUS_LABELS).map(([value, label]) => ({ value, label })),
];

export default function AdminOrdersPage() {
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const status = searchParams.get('status') ?? '';
  const page = Number(searchParams.get('page') ?? '1');

  const { data, loading, error, refetch, setData } = useFetch(
    () => transactionsApi.list({ status: status || undefined, ordering: '-created_date', page }),
    [status, page]
  );

  function handleStatusFilterChange(value) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set('status', value);
    else next.delete('status');
    next.delete('page');
    setSearchParams(next);
  }

  function handleUpdated(updated) {
    setData((current) => ({
      ...current,
      results: current.results.map((row) => (row.id === updated.id ? updated : row)),
    }));
  }

  const columns = [
    {
      key: 'transaction_number',
      header: 'Order',
      render: (row) => <span className="font-mono text-xs text-ink-500">#{String(row.transaction_number).slice(0, 8)}</span>,
    },
    { key: 'user_email', header: 'Customer' },
    { key: 'items', header: 'Items', render: (row) => pluralize(row.items.length, 'item') },
    { key: 'total_amount', header: 'Total', render: (row) => formatCurrency(row.total_amount) },
    { key: 'created_date', header: 'Placed', render: (row) => formatDate(row.created_date) },
    { key: 'status', header: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    {
      key: 'actions',
      header: '',
      render: (row) => <RowActions transaction={row} onUpdated={handleUpdated} onError={(err) => toast.error(err)} />,
    },
  ];

  return (
    <div>
      <PageHeader
        title="Orders"
        action={
          <Select
            aria-label="Filter by status"
            options={STATUS_FILTER_OPTIONS}
            value={status}
            onChange={(event) => handleStatusFilterChange(event.target.value)}
            className="w-48"
          />
        }
      />

      <DataTable
        columns={columns}
        rows={data?.results ?? []}
        loading={loading}
        error={error}
        onRetry={refetch}
        emptyTitle="No orders found"
      />

      <Pagination pagination={data} onPageChange={(next) => setSearchParams({ ...(status && { status }), page: next })} className="mt-4" />
    </div>
  );
}

function RowActions({ transaction, onUpdated, onError }) {
  const [status, setStatus] = useState('');
  const { run, loading } = useAsync();

  async function handleUpdate() {
    if (!status) return;
    try {
      const updated = await run(() => transactionsApi.updateStatus(transaction.id, status));
      onUpdated(updated);
      setStatus('');
    } catch (err) {
      onError(getErrorMessage(err, 'Could not update this order.'));
    }
  }

  return (
    <div className="flex items-center justify-end gap-1.5">
      <Select
        aria-label={`Change status for order ${transaction.transaction_number}`}
        placeholder="Set status"
        options={Object.entries(ORDER_STATUS_LABELS).map(([value, label]) => ({ value, label }))}
        value={status}
        onChange={(event) => setStatus(event.target.value)}
        className="h-8 w-36 text-xs"
      />
      <Button size="sm" variant="outline" onClick={handleUpdate} loading={loading} disabled={!status}>
        Apply
      </Button>
      <Button as={Link} to={`/orders/${transaction.id}`} variant="ghost" size="icon" aria-label="View order">
        <Eye className="h-4 w-4" aria-hidden="true" />
      </Button>
    </div>
  );
}
