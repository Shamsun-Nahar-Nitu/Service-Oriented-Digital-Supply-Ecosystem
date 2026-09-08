import { cn } from '../../utils/cn';

/**
 * Standard "nothing here" panel. Every list view (products, orders,
 * inventory, users) should render this instead of an empty <div> so empty
 * results always explain what happened and, where possible, what to do
 * next — see the copy guidance to treat emptiness as direction, not silence.
 */
export function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-ink-200 bg-white px-6 py-16 text-center',
        className
      )}
    >
      {Icon && (
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-ink-100 text-ink-400">
          <Icon className="h-6 w-6" aria-hidden="true" />
        </div>
      )}
      <h3 className="text-base font-semibold text-ink-900">{title}</h3>
      {description && <p className="max-w-sm text-sm text-ink-500">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
