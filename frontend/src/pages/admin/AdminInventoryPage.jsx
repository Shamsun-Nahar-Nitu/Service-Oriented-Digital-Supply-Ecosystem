import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PackagePlus, History } from 'lucide-react';
import { inventoryApi } from '../../api/inventory';
import { useFetch } from '../../hooks/useFetch';
import { useAsync } from '../../hooks/useAsync';
import { useDebounce } from '../../hooks/useDebounce';
import { useToast } from '../../context/ToastContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Input } from '../../components/ui/Input';
import { DataTable } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { Pagination } from '../../components/ui/Pagination';
import { formatDateTime } from '../../utils/format';
import { getErrorMessage } from '../../utils/errors';
import { STOCK_MOVEMENT_LABELS } from '../../utils/constants';

export default function AdminInventoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get('page') ?? '1');
  const [searchInput, setSearchInput] = useState('');
  const debouncedSearch = useDebounce(searchInput, 400);
  const [restockTarget, setRestockTarget] = useState(null);
  const [movementsTarget, setMovementsTarget] = useState(null);

  const { data, loading, error, refetch } = useFetch(
    () => inventoryApi.list({ search: debouncedSearch || undefined, ordering: 'quantity_in_stock', page }),
    [debouncedSearch, page]
  );

  const columns = [
    { key: 'product_name', header: 'Product', render: (row) => <span className="font-medium text-ink-900">{row.product_name}</span> },
    { key: 'sku', header: 'SKU' },
    { key: 'quantity_in_stock', header: 'In stock' },
    { key: 'reorder_level', header: 'Reorder at' },
    {
      key: 'status',
      header: 'Status',
      render: (row) =>
        row.quantity_in_stock === 0 ? (
          <Badge tone="danger">Out of stock</Badge>
        ) : row.is_low_stock ? (
          <Badge tone="gold">Low stock</Badge>
        ) : (
          <Badge tone="success">Healthy</Badge>
        ),
    },
    { key: 'last_restocked_at', header: 'Last restocked', render: (row) => formatDateTime(row.last_restocked_at) },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" aria-label={`Restock ${row.product_name}`} onClick={() => setRestockTarget(row)}>
            <PackagePlus className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button variant="ghost" size="icon" aria-label={`View movement history for ${row.product_name}`} onClick={() => setMovementsTarget(row)}>
            <History className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader title="Inventory" description="Stock levels across every vendor's catalog." />

      <Input
        placeholder="Search by product name or SKU…"
        value={searchInput}
        onChange={(event) => setSearchInput(event.target.value)}
        className="mb-4 max-w-sm"
      />

      <DataTable
        columns={columns}
        rows={data?.results ?? []}
        loading={loading}
        error={error}
        onRetry={refetch}
        emptyTitle="No inventory records found"
      />

      <Pagination pagination={data} onPageChange={(next) => setSearchParams({ page: next })} className="mt-4" />

      <RestockModal
        target={restockTarget}
        onClose={() => setRestockTarget(null)}
        onRestocked={() => {
          setRestockTarget(null);
          refetch();
        }}
      />
      <MovementsModal target={movementsTarget} onClose={() => setMovementsTarget(null)} />
    </div>
  );
}

function RestockModal({ target, onClose, onRestocked }) {
  const toast = useToast();
  const { run, loading, error } = useAsync();
  const [quantity, setQuantity] = useState('');
  const [note, setNote] = useState('');

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      await run(() => inventoryApi.restock(target.id, { quantity: Number(quantity), note }));
      toast.success(`Added ${quantity} unit(s) to ${target.product_name}.`);
      setQuantity('');
      setNote('');
      onRestocked();
    } catch {
      // Error surfaced inline below via `error`.
    }
  }

  return (
    <Modal open={Boolean(target)} onClose={onClose} title={target && `Restock ${target.product_name}`} size="sm">
      {target && (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <p className="text-sm text-ink-500">Currently {target.quantity_in_stock} in stock.</p>
          <Input
            label="Quantity to add"
            type="number"
            min="1"
            required
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
          />
          <Input label="Note (optional)" value={note} onChange={(event) => setNote(event.target.value)} />
          {error && <p className="text-sm text-danger-600">{getErrorMessage(error)}</p>}
          <Button type="submit" loading={loading}>
            Confirm restock
          </Button>
        </form>
      )}
    </Modal>
  );
}

function MovementsModal({ target, onClose }) {
  const { data, loading, error } = useFetch(() => inventoryApi.movements(target.id), [target?.id], {
    skip: !target,
  });

  return (
    <Modal open={Boolean(target)} onClose={onClose} title={target && `Stock history — ${target.product_name}`} size="lg">
      {loading && <p className="text-sm text-ink-500">Loading history…</p>}
      {error && <p className="text-sm text-danger-600">{getErrorMessage(error)}</p>}
      {data && data.length === 0 && <p className="text-sm text-ink-500">No stock movements recorded yet.</p>}
      {data && data.length > 0 && (
        <ul className="max-h-96 divide-y divide-ink-100 overflow-y-auto">
          {data.map((movement) => (
            <li key={movement.id} className="flex items-center justify-between py-2.5 text-sm">
              <div>
                <p className="font-medium text-ink-900">{STOCK_MOVEMENT_LABELS[movement.movement_type]}</p>
                {movement.note && <p className="text-ink-500">{movement.note}</p>}
                <p className="text-xs text-ink-400">{formatDateTime(movement.created_date)}</p>
              </div>
              <span className={movement.quantity >= 0 ? 'font-semibold text-success-600' : 'font-semibold text-danger-600'}>
                {movement.quantity >= 0 ? '+' : ''}
                {movement.quantity}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Modal>
  );
}
