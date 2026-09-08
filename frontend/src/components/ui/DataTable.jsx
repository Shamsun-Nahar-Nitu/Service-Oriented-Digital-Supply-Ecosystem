import { SkeletonRow } from './Skeleton';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { Inbox } from 'lucide-react';

/**
 * Generic data table used across every admin/vendor list screen (products,
 * inventory, orders, users). Columns are declarative so each page only
 * describes *what* to show, not how to render loading/empty/error states —
 * that behavior is defined once, here.
 */
export function DataTable({
  columns,
  rows,
  loading,
  error,
  onRetry,
  getRowKey = (row) => row.id,
  emptyTitle = 'Nothing here yet',
  emptyDescription,
  skeletonRows = 5,
}) {
  if (error) {
    return <ErrorState error={error} onRetry={onRetry} className="my-4" />;
  }

  return (
    <div className="overflow-hidden rounded-xl border border-ink-100 bg-white">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-ink-100 bg-ink-50/60">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className="whitespace-nowrap px-4 py-3 font-medium text-ink-500"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-100">
            {loading &&
              Array.from({ length: skeletonRows }).map((_, index) => (
                // eslint-disable-next-line react/no-array-index-key
                <SkeletonRow key={index} columns={columns.length} />
              ))}
            {!loading &&
              rows.map((row) => (
                <tr key={getRowKey(row)} className="hover:bg-ink-50/50">
                  {columns.map((column) => (
                    <td key={column.key} className="px-4 py-3 align-middle text-ink-800">
                      {column.render ? column.render(row) : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))}
          </tbody>
        </table>
      </div>
      {!loading && rows.length === 0 && (
        <EmptyState icon={Inbox} title={emptyTitle} description={emptyDescription} className="border-none" />
      )}
    </div>
  );
}
