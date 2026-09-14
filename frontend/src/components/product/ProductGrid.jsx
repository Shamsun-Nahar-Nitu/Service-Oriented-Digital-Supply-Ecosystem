import { PackageSearch } from 'lucide-react';
import { ProductCard } from './ProductCard';
import { SkeletonProductCard } from '../ui/Skeleton';
import { EmptyState } from '../ui/EmptyState';
import { ErrorState } from '../ui/ErrorState';

/**
 * Renders a responsive product grid with loading skeletons, an empty
 * state, and an error state — every page that lists products (home,
 * catalog, vendor's own listings, related items) shares this so the three
 * non-happy-path states never get forgotten on a new page.
 */
export function ProductGrid({
  products,
  loading,
  error,
  onRetry,
  skeletonCount = 8,
  emptyTitle = 'No products found',
  emptyDescription = 'Try a different search term or clear your filters.',
}) {
  if (error) {
    return <ErrorState error={error} onRetry={onRetry} className="my-6" />;
  }

  if (!loading && products.length === 0) {
    return (
      <EmptyState
        icon={PackageSearch}
        title={emptyTitle}
        description={emptyDescription}
        className="my-6"
      />
    );
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5">
      {loading
        ? Array.from({ length: skeletonCount }).map((_, index) => (
            <SkeletonProductCard key={index} />
          ))
        : products.map((product) => <ProductCard key={product.id} product={product} />)}
    </div>
  );
}
