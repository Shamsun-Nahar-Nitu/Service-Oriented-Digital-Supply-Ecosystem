import { Minus, Plus } from 'lucide-react';
import { cn } from '../../utils/cn';

/**
 * Shared +/- quantity control used on the product detail page and in the
 * cart. `max` should be the product's live quantity_in_stock so a person
 * can never step past what's actually available.
 */
export function QuantityStepper({ value, onChange, min = 1, max, className, disabled }) {
  const atMin = value <= min;
  const atMax = typeof max === 'number' && value >= max;

  function handleInputChange(event) {
    const next = Number(event.target.value.replace(/[^0-9]/g, ''));
    if (Number.isNaN(next)) return;
    const clamped = Math.max(min, typeof max === 'number' ? Math.min(next, max) : next);
    onChange(clamped);
  }

  return (
    <div
      className={cn(
        'inline-flex h-10 items-center rounded-lg border border-ink-200 bg-white',
        disabled && 'opacity-50',
        className
      )}
    >
      <button
        type="button"
        onClick={() => onChange(Math.max(min, value - 1))}
        disabled={disabled || atMin}
        aria-label="Decrease quantity"
        className="flex h-full w-9 items-center justify-center text-ink-600 hover:bg-ink-50 disabled:pointer-events-none disabled:opacity-40"
      >
        <Minus className="h-3.5 w-3.5" aria-hidden="true" />
      </button>
      <input
        type="text"
        inputMode="numeric"
        value={value}
        onChange={handleInputChange}
        disabled={disabled}
        aria-label="Quantity"
        className="h-full w-10 border-x border-ink-200 text-center text-sm font-medium text-ink-900 focus-visible:outline-none"
      />
      <button
        type="button"
        onClick={() => onChange(typeof max === 'number' ? Math.min(max, value + 1) : value + 1)}
        disabled={disabled || atMax}
        aria-label="Increase quantity"
        className="flex h-full w-9 items-center justify-center text-ink-600 hover:bg-ink-50 disabled:pointer-events-none disabled:opacity-40"
      >
        <Plus className="h-3.5 w-3.5" aria-hidden="true" />
      </button>
    </div>
  );
}
