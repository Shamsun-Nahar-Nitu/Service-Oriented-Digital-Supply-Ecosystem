import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

/**
 * Matches the pagination envelope every list endpoint returns (see
 * apps/core/pagination.py::DefaultPagination): { count, total_pages,
 * current_page, next, previous, results }. Pass the raw pagination object
 * plus a page-change handler; this component figures out button states.
 */
export function Pagination({ pagination, onPageChange, className }) {
  if (!pagination || pagination.total_pages <= 1) return null;

  const { current_page: current, total_pages: total } = pagination;

  return (
    <nav aria-label="Pagination" className={className}>
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-ink-500">
          Page {current} of {total} · {pagination.count} results
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(current - 1)}
            disabled={!pagination.previous}
            aria-label="Previous page"
          >
            <ChevronLeft className="h-4 w-4" aria-hidden="true" />
            Prev
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(current + 1)}
            disabled={!pagination.next}
            aria-label="Next page"
          >
            Next
            <ChevronRight className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
    </nav>
  );
}
