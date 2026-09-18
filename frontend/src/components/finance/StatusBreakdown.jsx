import { StatusBadge } from '../ui/StatusBadge';

/** Renders an `orders_by_status` list — [{ status, count }, ...] — as
 * horizontal bars scaled to the largest count, so relative volume is
 * readable at a glance without needing a full chart for six numbers. */
export function StatusBreakdown({ data }) {
  if (!data || data.length === 0) {
    return <p className="py-6 text-center text-sm text-ink-500">No orders in this period.</p>;
  }

  const max = Math.max(...data.map((row) => row.count), 1);

  return (
    <ul className="space-y-2.5">
      {data.map((row) => (
        <li key={row.status} className="flex items-center gap-3">
          <StatusBadge status={row.status} className="w-24 shrink-0 justify-center" />
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-ink-50">
            <div
              className="h-full rounded-full bg-ember-500"
              style={{ width: `${(row.count / max) * 100}%` }}
            />
          </div>
          <span className="w-8 shrink-0 text-right text-sm font-semibold text-ink-800">{row.count}</span>
        </li>
      ))}
    </ul>
  );
}