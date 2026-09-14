import { cn } from '../../utils/cn';

/** Base pulsing placeholder block; compose into shapes for specific loading states. */
export function Skeleton({ className }) {
  return <div className={cn('animate-pulse rounded-md bg-ink-100', className)} />;
}

export function SkeletonText({ lines = 1, className }) {
  return (
    <div className="flex flex-col gap-2">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          className={cn('h-3', index === lines - 1 && lines > 1 ? 'w-2/3' : 'w-full', className)}
        />
      ))}
    </div>
  );
}

/** Placeholder matching <ProductCard />'s layout, for grid loading states. */
export function SkeletonProductCard() {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-ink-100 bg-white p-3">
      <Skeleton className="aspect-square w-full rounded-lg" />
      <Skeleton className="h-3 w-1/3" />
      <SkeletonText lines={2} />
      <Skeleton className="h-5 w-1/2" />
    </div>
  );
}

/** Placeholder matching a table row, for dashboard list loading states. */
export function SkeletonRow({ columns = 4 }) {
  return (
    <tr>
      {Array.from({ length: columns }).map((_, index) => (
        <td key={index} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
}
