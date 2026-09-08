import { cn } from '../../utils/cn';
import {
  ORDER_STATUS_LABELS,
  ORDER_STATUS_STYLES,
  PAYMENT_STATUS_STYLES,
} from '../../utils/constants';

/** Renders a Transaction.status or Payment.status value as a colored pill. */
export function StatusBadge({ status, kind = 'order', className }) {
  const styles = kind === 'payment' ? PAYMENT_STATUS_STYLES : ORDER_STATUS_STYLES;
  const label = kind === 'payment' ? titleCase(status) : ORDER_STATUS_LABELS[status] ?? status;

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
        styles[status] ?? 'bg-ink-100 text-ink-700',
        className
      )}
    >
      {label}
    </span>
  );
}

function titleCase(value) {
  if (!value) return '';
  return value[0] + value.slice(1).toLowerCase();
}
