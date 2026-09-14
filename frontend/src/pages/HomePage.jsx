import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Truck, Undo2 } from 'lucide-react';
import { productsApi } from '../api/products';
import { categoriesApi } from '../api/categories';
import { useFetch } from '../hooks/useFetch';
import { useAuth } from '../context/AuthContext';
import { ProductGrid } from '../components/product/ProductGrid';
import { ProductThumb } from '../components/ui/ProductThumb';
import { Button } from '../components/ui/Button';

export default function HomePage() {
  const { user } = useAuth();

  const {
    data: newArrivals,
    loading: productsLoading,
    error: productsError,
    refetch: refetchProducts,
  } = useFetch(() => productsApi.list({ ordering: '-created_date', page_size: 10, in_stock: true }), []);

  const { data: categoryData, loading: categoriesLoading } = useFetch(
    () => categoriesApi.list({ is_active: true, page_size: 100, ordering: 'name' }),
    []
  );

  const topCategories = (categoryData?.results ?? []).filter((category) => !category.parent).slice(0, 6);

  return (
    <div>
      <section className="bg-ink-900 text-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-12 sm:px-6 md:flex-row md:items-center md:py-16">
          <div className="flex-1">
            <p className="text-sm font-semibold uppercase tracking-wide text-ember-400">
              Welcome{user?.first_name ? `, ${user.first_name}` : ''}
            </p>
            <h1 className="mt-2 font-display text-3xl font-extrabold sm:text-4xl">
              Everything you need, from sellers you can trust.
            </h1>
            <p className="mt-3 max-w-lg text-ink-200">
              Browse a growing catalog from independent vendors — competitive prices, real stock
              levels, and orders you can track end to end.
            </p>
            <Button as={Link} to="/products" size="lg" className="mt-6">
              Start shopping
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Button>
          </div>
          <div className="grid flex-1 grid-cols-3 gap-3">
            {['#1F2645-#404B73', '#FF5A1F-#FF9E6B', '#B45400-#FFB020'].map((seed) => (
              <ProductThumb key={seed} seed={seed} iconOnly className="aspect-square" />
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-ink-100 bg-white">
        <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 sm:grid-cols-3 sm:px-6">
          <TrustPoint icon={Truck} title="Tracked delivery" description="Follow every order from placed to delivered." />
          <TrustPoint icon={ShieldCheck} title="Verified vendors" description="Every seller is a registered vendor account." />
          <TrustPoint icon={Undo2} title="Easy cancellation" description="Cancel a pending order in one click." />
        </div>
      </section>

      {topCategories.length > 0 && (
        <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
          <h2 className="font-display text-lg font-bold text-ink-900">Shop by category</h2>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-6">
            {categoriesLoading
              ? Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className="h-20 animate-pulse rounded-xl bg-ink-100" />
                ))
              : topCategories.map((category) => (
                  <Link
                    key={category.id}
                    to={`/products?category=${category.id}`}
                    className="flex h-20 flex-col items-center justify-center gap-1 rounded-xl border border-ink-100 bg-white px-2 text-center text-sm font-medium text-ink-700 transition-shadow hover:shadow-raised"
                  >
                    {category.name}
                  </Link>
                ))}
          </div>
        </section>
      )}

      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-lg font-bold text-ink-900">New arrivals</h2>
          <Link to="/products" className="text-sm font-medium text-ember-600 hover:underline">
            View all
          </Link>
        </div>
        <ProductGrid
          products={newArrivals?.results ?? []}
          loading={productsLoading}
          error={productsError}
          onRetry={refetchProducts}
          skeletonCount={10}
          emptyTitle="No products in stock yet"
          emptyDescription="Check back soon, or browse the full catalog."
        />
      </section>
    </div>
  );
}

function TrustPoint({ icon: Icon, title, description }) {
  return (
    <div className="flex items-start gap-3">
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-ember-50 text-ember-600">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <div>
        <p className="text-sm font-semibold text-ink-900">{title}</p>
        <p className="text-sm text-ink-500">{description}</p>
      </div>
    </div>
  );
}
