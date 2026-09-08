import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { productsApi } from '../../api/products';
import { categoriesApi } from '../../api/categories';
import { useFetch } from '../../hooks/useFetch';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { ProductForm } from '../../components/forms/ProductForm';
import { PageHeader } from '../../components/ui/PageHeader';
import { PageSpinner } from '../../components/ui/Spinner';
import { ErrorState } from '../../components/ui/ErrorState';

export default function VendorProductFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { user } = useAuth();
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

  if (isEdit && loading) return <PageSpinner label="Loading product…" />;
  if (isEdit && error) {
    return <ErrorState error={error} title="Couldn't load this product" className="my-12" />;
  }
  // A vendor can view other vendors' active listings via the shared /products/
  // queryset, but only their own are editable — catch the mismatch here with
  // a clear message rather than letting the PATCH fail on submit.
  if (isEdit && product && product.vendor !== user.id) {
    return (
      <ErrorState
        error={{ response: { data: { errors: { detail: "This product belongs to another vendor's catalog." } } } }}
        title="Not your product"
        className="my-12"
      />
    );
  }

  async function handleSubmit(payload) {
    const saved = isEdit ? await productsApi.update(id, payload) : await productsApi.create(payload);
    toast.success(isEdit ? 'Product updated.' : 'Product created.');
    navigate('/vendor/products');
    return saved;
  }

  return (
    <div>
      <Link to="/vendor/products" className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-ink-500 hover:text-ink-800">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Back to my products
      </Link>
      <PageHeader title={isEdit ? 'Edit product' : 'Add a product'} />
      <div className="max-w-2xl rounded-xl border border-ink-100 bg-white p-6">
        <ProductForm
          product={isEdit ? product : null}
          categories={categoryData?.results ?? []}
          categoriesLoading={categoriesLoading}
          vendorOptions={[]}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
  );
}
