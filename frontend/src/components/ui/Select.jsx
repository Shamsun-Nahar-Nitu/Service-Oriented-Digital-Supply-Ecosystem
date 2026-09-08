import { forwardRef, useId } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../utils/cn';

/**
 * Styled native <select>. Deliberately not a custom listbox — a native
 * select gets correct keyboard handling, screen reader support, and mobile
 * picker UI for free, which is worth more here than custom styling.
 */
export const Select = forwardRef(function Select(
  { label, error, hint, required, options = [], placeholder, className, id, ...props },
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
        <select
          id={inputId}
          ref={ref}
          required={required}
          aria-invalid={Boolean(error)}
          aria-describedby={cn(errorId, hintId) || undefined}
          className={cn(
            'h-10 w-full appearance-none rounded-lg border bg-white pl-3 pr-9 text-sm text-ink-900',
            'transition-colors focus-visible:border-ember-500',
            error ? 'border-danger-500' : 'border-ink-200 hover:border-ink-300',
            className
          )}
          {...props}
        >
          {placeholder && (
            <option value="" disabled={required}>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown
          className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400"
          aria-hidden="true"
        />
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
