import { forwardRef, useId } from 'react';
import { cn } from '../../utils/cn';

export const Textarea = forwardRef(function Textarea(
  { label, error, hint, required, className, id, rows = 4, ...props },
  ref
) {
  const autoId = useId();
  const inputId = id || autoId;
  const errorId = error ? `${inputId}-error` : undefined;
  const hintId = hint ? `${inputId}-hint` : undefined;

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-ink-800">
          {label}
          {required && (
            <span className="text-ember-600" aria-hidden="true">
              {' '}
              *
            </span>
          )}
        </label>
      )}
      <textarea
        id={inputId}
        ref={ref}
        rows={rows}
        required={required}
        aria-invalid={Boolean(error)}
        aria-describedby={cn(errorId, hintId) || undefined}
        className={cn(
          'w-full rounded-lg border bg-white px-3 py-2 text-sm text-ink-900 placeholder:text-ink-400',
          'transition-colors focus-visible:border-ember-500 resize-y',
          error ? 'border-danger-500' : 'border-ink-200 hover:border-ink-300',
          className
        )}
        {...props}
      />
      {error && (
        <p id={errorId} role="alert" className="text-sm text-danger-600">
          {error}
        </p>
      )}
      {!error && hint && (
        <p id={hintId} className="text-sm text-ink-500">
          {hint}
        </p>
      )}
    </div>
  );
});
