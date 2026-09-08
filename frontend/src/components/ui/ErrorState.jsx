import { AlertTriangle } from 'lucide-react';
import { Button } from './Button';
import { getErrorMessage } from '../../utils/errors';
import { cn } from '../../utils/cn';

/**
 * Standard "the request failed" panel with a retry action. Distinct from
 * EmptyState (which means "the request succeeded and there's nothing to
 * show") so people can tell a failure apart from a genuinely empty catalog.
 */
export function ErrorState({ error, onRetry, title = "Couldn't load this", className }) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 rounded-xl border border-danger-100 bg-danger-50 px-6 py-16 text-center',
        className
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-danger-100 text-danger-600">
        <AlertTriangle className="h-6 w-6" aria-hidden="true" />
      </div>
      <h3 className="text-base font-semibold text-ink-900">{title}</h3>
      <p className="max-w-sm text-sm text-ink-600">{getErrorMessage(error)}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} className="mt-1">
          Try again
        </Button>
      )}
    </div>
  );
}
