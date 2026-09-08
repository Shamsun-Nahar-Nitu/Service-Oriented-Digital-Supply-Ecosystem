import { useState } from 'react';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { categoriesApi } from '../../api/categories';
import { useFetch } from '../../hooks/useFetch';
import { useAsync } from '../../hooks/useAsync';
import { useToast } from '../../context/ToastContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';
import { DataTable } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { ConfirmDialog } from '../../components/ui/ConfirmDialog';
import { CategoryForm } from '../../components/forms/CategoryForm';
import { getErrorMessage } from '../../utils/errors';

export default function AdminCategoriesPage() {
  const toast = useToast();
  const { data, loading, error, refetch } = useFetch(
    () => categoriesApi.list({ page_size: 100, ordering: 'name' }),
    []
  );
  const [formTarget, setFormTarget] = useState(null); // null = closed, {} = create, category = edit
  const [pendingDelete, setPendingDelete] = useState(null);
  const deleteAction = useAsync();

  const categories = data?.results ?? [];

  async function handleSubmit(payload) {
    const saved = formTarget.id
      ? await categoriesApi.update(formTarget.id, payload)
      : await categoriesApi.create(payload);
    toast.success(formTarget.id ? 'Category updated.' : 'Category created.');
    setFormTarget(null);
    refetch();
    return saved;
  }

  async function handleDelete() {
    try {
      await deleteAction.run(() => categoriesApi.remove(pendingDelete.id));
      toast.success(`"${pendingDelete.name}" was deleted.`);
      setPendingDelete(null);
      refetch();
    } catch (err) {
      toast.error(
        getErrorMessage(
          err,
          'Could not delete this category — it may still have products assigned to it.'
        )
      );
    }
  }

  const columns = [
    { key: 'name', header: 'Name', render: (row) => <span className="font-medium text-ink-900">{row.name}</span> },
    { key: 'code', header: 'Code' },
    { key: 'parent_name', header: 'Parent', render: (row) => row.parent_name || '—' },
    { key: 'subcategory_count', header: 'Subcategories' },
    {
      key: 'is_active',
      header: 'Status',
      render: (row) => <Badge tone={row.is_active ? 'success' : 'neutral'}>{row.is_active ? 'Active' : 'Inactive'}</Badge>,
    },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" aria-label={`Edit ${row.name}`} onClick={() => setFormTarget(row)}>
            <Pencil className="h-4 w-4" aria-hidden="true" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Delete ${row.name}`}
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
        title="Categories"
        action={
          <Button onClick={() => setFormTarget({})}>
            <Plus className="h-4 w-4" aria-hidden="true" /> Add category
          </Button>
        }
      />

      <DataTable
        columns={columns}
        rows={categories}
        loading={loading}
        error={error}
        onRetry={refetch}
        emptyTitle="No categories yet"
        emptyDescription="Add your first category to start organizing the catalog."
      />

      <Modal
        open={Boolean(formTarget)}
        onClose={() => setFormTarget(null)}
        title={formTarget?.id ? 'Edit category' : 'Add category'}
        size="lg"
      >
        {formTarget && (
          <CategoryForm category={formTarget.id ? formTarget : null} categories={categories} onSubmit={handleSubmit} />
        )}
      </Modal>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        onClose={() => setPendingDelete(null)}
        onConfirm={handleDelete}
        loading={deleteAction.loading}
        title="Delete this category?"
        description={pendingDelete && `"${pendingDelete.name}" will be permanently removed.`}
        confirmLabel="Delete"
      />
    </div>
  );
}
