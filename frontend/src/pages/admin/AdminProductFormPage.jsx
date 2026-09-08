import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { productsApi } from '../../api/products';
import { categoriesApi } from '../../api/categories';
import { adminUsersApi } from '../../api/auth';
import { useFetch } from '../../hooks/useFetch';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { ProductForm } from '../../components/forms/ProductForm';
import { PageHeader } from '../../components/ui/PageHeader';
import { PageSpinner } from '../../components/ui/Spinner';
import { ErrorState } from '../../components/ui/ErrorState';

export default function AdminProductFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const toast = useToast();

  const {
    data: product,
    loading,
    error,
  } = useFetch(() => productsApi.retrieve(id), [id], { skip: !isEdit });

  const { data: categoryData, loading: categoriesLoading } = useFetch(
    () => categoriesApi.list({ is_active: true, page_size: 100, ordering: 'name' }),
    []
  );

  // Browsing the vendor list is admin-only server-side (/auth/users/ requires
  // IsAdminRole), so managers simply don't get this lookup — ProductForm
  // falls back to a plain numeric vendor-ID field for them.
  const { data: vendorData } = useFetch(
    () => adminUsersApi.list({ role: 'VENDOR', page_size: 100, is_active: true }),
    [],
    { skip: !isAdmin }
  );

  if (isEdit && loading) return <PageSpinner label="Loading product…" />;
  if (isEdit && error) {
    return <ErrorState error={error} title="Couldn't load this product" className="my-12" />;
  }

  async function handleSubmit(payload) {
    const saved = isEdit ? await productsApi.update(id, payload) : await productsApi.create(payload);
    toast.success(isEdit ? 'Product updated.' : 'Product created.');
    navigate('/admin/products');
    return saved;
  }

  return (
    <div>
      <Link to="/admin/products" className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-ink-500 hover:text-ink-800">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Back to products
      </Link>
      <PageHeader title={isEdit ? 'Edit product' : 'Add a product'} />
      <div className="max-w-2xl rounded-xl border border-ink-100 bg-white p-6">
        <ProductForm
          product={isEdit ? product : null}
          categories={categoryData?.results ?? []}
          categoriesLoading={categoriesLoading}
          vendorOptions={vendorData?.results ?? []}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
  );
}
