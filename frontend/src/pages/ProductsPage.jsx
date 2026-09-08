import { useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SlidersHorizontal } from 'lucide-react';
import { productsApi } from '../api/products';
import { categoriesApi } from '../api/categories';
import { useFetch } from '../hooks/useFetch';
import { useDebounce } from '../hooks/useDebounce';
import { ProductGrid } from '../components/product/ProductGrid';
import { ProductFilters } from '../components/product/ProductFilters';
import { ProductSort } from '../components/product/ProductSort';
import { Pagination } from '../components/ui/Pagination';
import { Badge } from '../components/ui/Badge';

/**
 * The URL query string is the single source of truth for every filter, so
 * a page refresh, a shared link, or the browser back button all reproduce
 * the exact same result set instead of resetting to defaults.
 */
export default function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const search = searchParams.get('search') ?? '';
  const category = searchParams.get('category') ?? '';
  const minPrice = searchParams.get('min_price') ?? '';
  const maxPrice = searchParams.get('max_price') ?? '';
  const inStock = searchParams.get('in_stock') === 'true';
  const ordering = searchParams.get('ordering') ?? '-created_date';
  const page = Number(searchParams.get('page') ?? '1');

  // Price inputs are debounced so every keystroke doesn't fire a request —
  // only the settled value gets written into the URL / query params.
  const debouncedMinPrice = useDebounce(minPrice, 500);
  const debouncedMaxPrice = useDebounce(maxPrice, 500);

  function patchParams(patch) {
    const next = new URLSearchParams(searchParams);
    Object.entries(patch).forEach(([key, value]) => {
      if (value === '' || value === null || value === undefined || value === false) {
        next.delete(key);
      } else {
        next.set(key, String(value));
      }
    });
    // Any filter change other than paging itself should reset to page 1.
    if (!('page' in patch)) next.delete('page');
    setSearchParams(next);
  }

  const queryParams = useMemo(
    () => ({
      search: search || undefined,
      category: category || undefined,
      min_price: debouncedMinPrice || undefined,
      max_price: debouncedMaxPrice || undefined,
      in_stock: inStock || undefined,
      ordering,
      page,
    }),
    [search, category, debouncedMinPrice, debouncedMaxPrice, inStock, ordering, page]
  );

  const {
    data,
    loading,
    error,
    refetch: refetchProducts,
  } = useFetch(() => productsApi.list(queryParams), [JSON.stringify(queryParams)]);

  const { data: categoryData, loading: categoriesLoading } = useFetch(
    () => categoriesApi.list({ is_active: true, page_size: 100, ordering: 'name' }),
    []
  );

  const categories = categoryData?.results ?? [];
  const selectedCategory = categories.find((c) => String(c.id) === category);

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <h1 className="font-display text-xl font-bold text-ink-900">
          {search ? `Results for "${search}"` : selectedCategory ? selectedCategory.name : 'All products'}
        </h1>
        {data && <span className="text-sm text-ink-400">({data.count})</span>}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[240px_1fr]">
        <aside className="hidden lg:block">
          <ProductFilters
            categories={categories}
            categoriesLoading={categoriesLoading}
            values={{ category, minPrice, maxPrice, inStock }}
            onChange={(patch) =>
              patchParams({
                category: patch.category,
                min_price: patch.minPrice,
                max_price: patch.maxPrice,
                in_stock: patch.inStock,
              })
            }
            onClear={() => setSearchParams(search ? { search } : {})}
          />
        </aside>

        <div>
          <div className="mb-4 flex items-center justify-between gap-3">
            <details className="lg:hidden">
              <summary className="flex cursor-pointer list-none items-center gap-1.5 rounded-lg border border-ink-200 px-3 py-1.5 text-sm font-medium text-ink-700">
                <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
                Filters
                {(category || minPrice || maxPrice || inStock) && (
                  <Badge tone="ember" className="ml-1">
                    On
                  </Badge>
                )}
              </summary>
              <div className="mt-3 rounded-xl border border-ink-100 bg-white p-4">
                <ProductFilters
                  categories={categories}
                  categoriesLoading={categoriesLoading}
                  values={{ category, minPrice, maxPrice, inStock }}
                  onChange={(patch) =>
                    patchParams({
                      category: patch.category,
                      min_price: patch.minPrice,
                      max_price: patch.maxPrice,
                      in_stock: patch.inStock,
                    })
                  }
                  onClear={() => setSearchParams(search ? { search } : {})}
                />
              </div>
            </details>
            <div className="ml-auto">
              <ProductSort value={ordering} onChange={(value) => patchParams({ ordering: value })} />
            </div>
          </div>

          <ProductGrid
            products={data?.results ?? []}
            loading={loading}
            error={error}
            onRetry={refetchProducts}
            emptyDescription={
              search
                ? `No products matched "${search}". Try a different term or clear your filters.`
                : 'Try a different category or clear your filters.'
            }
          />

          <Pagination
            pagination={data}
            onPageChange={(nextPage) => patchParams({ page: nextPage })}
            className="mt-6"
          />
        </div>
      </div>
    </div>
  );
}
