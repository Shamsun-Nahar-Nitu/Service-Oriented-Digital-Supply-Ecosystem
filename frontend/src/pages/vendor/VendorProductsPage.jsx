import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { productsApi } from '../../api/products';
import { useFetch } from '../../hooks/useFetch';
import { useAsync } from '../../hooks/useAsync';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';
import { DataTable } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { Pagination } from '../../components/ui/Pagination';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { formatCurrency } from '../../utils/format';
import { getErrorMessage } from '../../utils/errors';

export default function VendorProductsPage() {
  const { user } = useAuth();
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get('page') ?? '1');
  const [pendingDelete, setPendingDelete] = useState(null);
  const deleteAction = useAsync();

  const { data, loading, error, refetch } = useFetch(
    () => productsApi.list({ vendor: user.id, ordering: '-created_date', page }),
    [user.id, page]
  );

  async function handleDelete() {
    try {
      await deleteAction.run(() => productsApi.remove(pendingDelete.id));
      toast.success(`"${pendingDelete.product_name}" was deleted.`);
      setPendingDelete(null);
      refetch();
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not delete this product.'));
    }
  }

  const columns = [
    { key: 'product_name', header: 'Product', render: (row) => <span className="font-medium text-ink-900">{row.product_name}</span> },
    { key: 'sku', header: 'SKU' },
    { key: 'category_name', header: 'Category' },
    { key: 'selling_price', header: 'Price', render: (row) => formatCurrency(row.selling_price) },
    { key: 'quantity_in_stock', header: 'Stock' },
    {
      key: 'status',
      header: 'Status',
      render: (row) => (
        <div className="flex flex-wrap gap-1.5">
          <Badge tone={row.is_active ? 'success' : 'neutral'}>{row.is_active ? 'Active' : 'Inactive'}</Badge>
          {row.issues !== 'NONE' && <Badge tone="danger">Flagged</Badge>}
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex justify-end gap-1">
          <Button as={Link} to={`/vendor/products/${row.id}/edit`} variant="ghost" size="icon" aria-label={`Edit ${row.product_name}`}>
            <Pencil className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Delete ${row.product_name}`}
            className="text-danger-600 hover:bg-danger-50"
            onClick={() => setPendingDelete(row)}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="My products"
        description="Products you list are only visible to shoppers once marked active."
        action={
          <Button as={Link} to="/vendor/products/new">
            <Plus className="h-4 w-4" aria-hidden="true" /> Add product
          </Button>
        }
      />

      <DataTable
        columns={columns}
        rows={data?.results ?? []}
        loading={loading}
        error={error}
        onRetry={refetch}
        emptyTitle="You haven't listed any products yet"
        emptyDescription="Add your first product to start selling."
      />

      <Pagination pagination={data} onPageChange={(next) => setSearchParams({ page: next })} className="mt-4" />

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        onClose={() => setPendingDelete(null)}
        onConfirm={handleDelete}
        loading={deleteAction.loading}
        title="Delete this product?"
        description={pendingDelete && `"${pendingDelete.product_name}" will be permanently removed from your catalog.`}
        confirmLabel="Delete"
      />
    </div>
  );
}
