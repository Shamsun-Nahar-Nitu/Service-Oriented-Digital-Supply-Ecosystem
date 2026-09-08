import { cn } from '../../utils/cn';

const TONES = {
  neutral: 'bg-ink-100 text-ink-700',
  ember: 'bg-ember-100 text-ember-700',
  gold: 'bg-gold-100 text-gold-700',
  success: 'bg-success-100 text-success-700',
  danger: 'bg-danger-100 text-danger-700',
};

/** Generic colored pill for counts, tags, and short labels. */
export function Badge({ tone = 'neutral', className, children, ...props }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        TONES[tone],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
