import { forwardRef, useId } from 'react';
import { cn } from '../../utils/cn';

export const Checkbox = forwardRef(function Checkbox({ label, className, id, ...props }, ref) {
  const autoId = useId();
  const inputId = id || autoId;

  return (
    <label htmlFor={inputId} className="flex items-center gap-2 text-sm text-ink-800 cursor-pointer select-none">
      <input
        id={inputId}
        ref={ref}
        type="checkbox"
        className={cn(
          'h-4 w-4 rounded border-ink-300 text-ember-500 focus-visible:ring-0',
          'accent-ember-500',
          className
        )}
        {...props}
      />
      {label}
    </label>
  );
});
