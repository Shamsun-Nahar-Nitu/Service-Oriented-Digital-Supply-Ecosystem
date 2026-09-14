import { Link, useSearchParams } from 'react-router-dom';
import { categoriesApi } from '../../api/categories';
import { useFetch } from '../../hooks/useFetch';
import { cn } from '../../utils/cn';

/**
 * Horizontal strip of top-level categories under the header. The
 * categories API has no "top-level only" filter, so this fetches a
 * generous page and filters out subcategories client-side — fine at
 * catalog sizes where categories number in the dozens, not thousands.
 *
 * Every endpoint in this API requires authentication, so this skips the
 * fetch entirely for guests instead of firing a request that's guaranteed
 * to 403.
 */
export function CategoryNav() {
  const [searchParams] = useSearchParams();
  const activeCategory = searchParams.get('category');
  const { data, loading } = useFetch(
    () => categoriesApi.list({ is_active: true, page_size: 100, ordering: 'name' }),
    []
  );

  const topLevel = (data?.results ?? []).filter((category) => !category.parent);

  if (!loading && topLevel.length === 0) return null;

  return (
    <nav aria-label="Categories" className="border-b border-ink-100 bg-white">
      <div className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-4 py-2 no-scrollbar sm:px-6">
        <Link
          to="/products"
          className={cn(
            'shrink-0 rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors',
            !activeCategory ? 'bg-ink-900 text-white' : 'text-ink-600 hover:bg-ink-100'
          )}
        >
          All
        </Link>
        {loading
          ? Array.from({ length: 6 }).map((_, index) => (
              <span key={index} className="h-8 w-24 shrink-0 animate-pulse rounded-full bg-ink-100" />
            ))
          : topLevel.map((category) => (
              <Link
                key={category.id}
                to={`/products?category=${category.id}`}
                className={cn(
                  'shrink-0 rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors',
                  String(activeCategory) === String(category.id)
                    ? 'bg-ink-900 text-white'
                    : 'text-ink-600 hover:bg-ink-100'
                )}
              >
                {category.name}
              </Link>
            ))}
      </div>
    </nav>
  );
}
