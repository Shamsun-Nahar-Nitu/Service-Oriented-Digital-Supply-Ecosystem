import { Check } from 'lucide-react';
import { ORDER_STATUS_LABELS, ORDER_STATUS_SEQUENCE } from '../../utils/constants';
import { cn } from '../../utils/cn';

/**
 * Visual progress tracker for the normal happy-path lifecycle (Pending →
 * Confirmed → Shipped → Delivered). Cancelled/refunded orders don't fit on
 * this line, so the caller should show a plain <StatusBadge /> instead when
 * status is one of those.
 */
export function OrderStatusTimeline({ status }) {
  const currentIndex = ORDER_STATUS_SEQUENCE.indexOf(status);

  return (
    <ol className="flex items-center">
      {ORDER_STATUS_SEQUENCE.map((step, index) => {
        const isComplete = index <= currentIndex;
        const isLast = index === ORDER_STATUS_SEQUENCE.length - 1;

        return (
          <li key={step} className="flex flex-1 items-center last:flex-none">
            <div className="flex flex-col items-center gap-2">
              <span
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-semibold',
                  isComplete
                    ? 'border-success-500 bg-success-500 text-white'
                    : 'border-ink-200 bg-white text-ink-400'
                )}
              >
                {isComplete ? <Check className="h-4 w-4" aria-hidden="true" /> : index + 1}
              </span>
              <span
                className={cn(
                  'whitespace-nowrap text-xs font-medium',
                  isComplete ? 'text-ink-900' : 'text-ink-400'
                )}
              >
                {ORDER_STATUS_LABELS[step]}
              </span>
            </div>
            {!isLast && (
              <div
                className={cn('mx-2 h-0.5 flex-1', index < currentIndex ? 'bg-success-500' : 'bg-ink-200')}
              />
            )}
          </li>
        );
      })}
    </ol>
  );
}
