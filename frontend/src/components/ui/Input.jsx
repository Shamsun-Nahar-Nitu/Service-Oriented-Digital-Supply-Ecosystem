import { forwardRef, useId } from 'react';
import { cn } from '../../utils/cn';

/**
 * Labeled text input with built-in error/hint rendering and correct
 * aria-describedby wiring, so every form in the app gets accessible error
 * announcements for free instead of each page re-implementing it.
 */
export const Input = forwardRef(function Input(
  { label, error, hint, required, leftIcon, rightIcon, className, id, ...props },
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
      <div className="relative">
        {leftIcon && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400 pointer-events-none">
            {leftIcon}
          </span>
        )}
        <input
          id={inputId}
          ref={ref}
          required={required}
          aria-invalid={Boolean(error)}
          aria-describedby={cn(errorId, hintId) || undefined}
          className={cn(
            'h-10 w-full rounded-lg border bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400',
            'transition-colors focus-visible:border-ember-500',
            error ? 'border-danger-500' : 'border-ink-200 hover:border-ink-300',
            leftIcon && 'pl-9',
            rightIcon && 'pr-9',
            className
          )}
          {...props}
        />
        {rightIcon && (
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-400">
            {rightIcon}
          </span>
        )}
      </div>
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
