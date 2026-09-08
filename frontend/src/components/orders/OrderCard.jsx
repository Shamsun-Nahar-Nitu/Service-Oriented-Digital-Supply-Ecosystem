import { Link } from 'react-router-dom';
import { StatusBadge } from '../ui/StatusBadge';
import { formatCurrency, formatDate, pluralize } from '../../utils/format';

/** Summary row for a single order, used on the customer's "My Orders" list. */
export function OrderCard({ transaction }) {
  return (
    <Link
      to={`/orders/${transaction.id}`}
      className="flex flex-col gap-3 rounded-xl border border-ink-100 bg-white p-4 transition-shadow hover:shadow-raised sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <p className="font-mono text-xs text-ink-400">
          #{String(transaction.transaction_number).slice(0, 8)}
        </p>
        <p className="mt-1 text-sm font-medium text-ink-900">
          {pluralize(transaction.items.length, 'item')} · Placed {formatDate(transaction.created_date)}
        </p>
        <p className="mt-1 line-clamp-1 text-sm text-ink-500">
          {transaction.items.map((item) => item.product_name).join(', ')}
        </p>
      </div>
      <div className="flex items-center justify-between gap-4 sm:flex-col sm:items-end sm:justify-start">
        <StatusBadge status={transaction.status} />
        <p className="font-display text-base font-semibold text-ink-900">
          {formatCurrency(transaction.total_amount)}
        </p>
      </div>
    </Link>
  );
}
