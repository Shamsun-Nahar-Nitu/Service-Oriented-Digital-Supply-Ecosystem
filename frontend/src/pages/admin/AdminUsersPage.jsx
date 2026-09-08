import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Plus, Pencil } from 'lucide-react';
import { adminUsersApi } from '../../api/auth';
import { useFetch } from '../../hooks/useFetch';
import { useToast } from '../../context/ToastContext';
import { PageHeader } from '../../components/ui/PageHeader';
import { Button } from '../../components/ui/Button';
import { Select } from '../../components/ui/Select';
import { DataTable } from '../../components/ui/DataTable';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Pagination } from '../../components/ui/Pagination';
import { UserForm } from '../../components/forms/UserForm';
import { ROLE_LABELS } from '../../utils/constants';
import { formatDate } from '../../utils/format';

const ROLE_FILTER_OPTIONS = [
  { value: '', label: 'All roles' },
  ...Object.entries(ROLE_LABELS).map(([value, label]) => ({ value, label })),
];

export default function AdminUsersPage() {
  const toast = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const role = searchParams.get('role') ?? '';
  const page = Number(searchParams.get('page') ?? '1');
  const [formTarget, setFormTarget] = useState(null);

  const { data, loading, error, refetch } = useFetch(
    () => adminUsersApi.list({ role: role || undefined, ordering: '-created_date', page }),
    [role, page]
  );

  function handleRoleFilterChange(value) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set('role', value);
    else next.delete('role');
    next.delete('page');
    setSearchParams(next);
  }

  async function handleSubmit(payload) {
    const saved = formTarget.id
      ? await adminUsersApi.update(formTarget.id, payload)
      : await adminUsersApi.create(payload);
    toast.success(formTarget.id ? 'Account updated.' : 'Account created.');
    setFormTarget(null);
    refetch();
    return saved;
  }

  const columns = [
    {
      key: 'name',
      header: 'Name',
      render: (row) => (
        <div>
          <p className="font-medium text-ink-900">{row.full_name || '—'}</p>
          <p className="text-xs text-ink-400">{row.email}</p>
        </div>
      ),
    },
    { key: 'role', header: 'Role', render: (row) => <Badge tone="neutral">{ROLE_LABELS[row.role]}</Badge> },
    {
      key: 'is_active',
      header: 'Status',
      render: (row) => <Badge tone={row.is_active ? 'success' : 'danger'}>{row.is_active ? 'Active' : 'Deactivated'}</Badge>,
    },
    { key: 'created_date', header: 'Joined', render: (row) => formatDate(row.created_date) },
    {
      key: 'actions',
      header: '',
      render: (row) => (
        <Button variant="ghost" size="icon" aria-label={`Edit ${row.email}`} onClick={() => setFormTarget(row)}>
          <Pencil className="h-4 w-4" aria-hidden="true" />
        </Button>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Users"
        description="Create manager/admin accounts and manage any user's role or access."
        action={
          <div className="flex gap-2">
            <Select
              aria-label="Filter by role"
              options={ROLE_FILTER_OPTIONS}
              value={role}
              onChange={(event) => handleRoleFilterChange(event.target.value)}
              className="w-40"
            />
            <Button onClick={() => setFormTarget({})}>
              <Plus className="h-4 w-4" aria-hidden="true" /> Add user
            </Button>
          </div>
        }
      />

      <DataTable columns={columns} rows={data?.results ?? []} loading={loading} error={error} onRetry={refetch} emptyTitle="No users found" />

      <Pagination pagination={data} onPageChange={(next) => setSearchParams({ ...(role && { role }), page: next })} className="mt-4" />

      <Modal open={Boolean(formTarget)} onClose={() => setFormTarget(null)} title={formTarget?.id ? 'Edit account' : 'Add account'} size="lg">
        {formTarget && <UserForm user={formTarget.id ? formTarget : null} onSubmit={handleSubmit} />}
      </Modal>
    </div>
  );
}
