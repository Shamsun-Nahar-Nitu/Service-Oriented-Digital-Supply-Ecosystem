import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

/** Standalone loading spinner for inline or full-section loading moments. */
export function Spinner({ size = 20, className, label = 'Loading' }) {
  return (
    <span role="status" className={cn('inline-flex items-center', className)}>
      <Loader2 style={{ width: size, height: size }} className="animate-spin text-ember-500" aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </span>
  );
}

export function PageSpinner({ label = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-24 text-ink-500">
      <Spinner size={28} />
      <p className="text-sm">{label}</p>
    </div>
  );
}
