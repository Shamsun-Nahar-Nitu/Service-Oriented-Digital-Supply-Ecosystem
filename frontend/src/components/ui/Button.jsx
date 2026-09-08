import { forwardRef } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

const VARIANTS = {
  primary: 'bg-ember-500 text-white hover:bg-ember-600 active:bg-ember-700 shadow-card',
  secondary: 'bg-ink-900 text-white hover:bg-ink-800 active:bg-ink-700',
  outline: 'border border-ink-200 text-ink-800 bg-white hover:bg-ink-50 active:bg-ink-100',
  ghost: 'text-ink-700 hover:bg-ink-100 active:bg-ink-200',
  danger: 'bg-danger-500 text-white hover:bg-danger-600 active:bg-danger-700',
  link: 'text-ember-600 hover:text-ember-700 underline-offset-4 hover:underline p-0 h-auto',
};

const SIZES = {
  sm: 'h-8 px-3 text-sm gap-1.5',
  md: 'h-10 px-4 text-sm gap-2',
  lg: 'h-12 px-6 text-base gap-2',
  icon: 'h-10 w-10 p-0 justify-center',
};

/**
 * The single button primitive for the app. Every visual button variant used
 * anywhere (add to cart, save, cancel, destructive actions) should route
 * through this component so hover/focus/disabled/loading behavior stays
 * consistent — no one-off `<button className="...">` scattered in pages.
 */
export const Button = forwardRef(function Button(
  {
    as: Component = 'button',
    variant = 'primary',
    size = 'md',
    loading = false,
    disabled = false,
    fullWidth = false,
    className,
    children,
    ...props
  },
  ref
) {
  const isDisabled = disabled || loading;

  return (
    <Component
      ref={ref}
      disabled={Component === 'button' ? isDisabled : undefined}
      aria-disabled={isDisabled}
      className={cn(
        'inline-flex items-center justify-center rounded-lg font-medium transition-colors duration-150',
        'disabled:opacity-50 disabled:pointer-events-none',
        VARIANTS[variant],
        SIZES[size],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
      {children}
    </Component>
  );
});
