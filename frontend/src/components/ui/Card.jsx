import { cn } from '../../utils/cn';

export function Card({ className, children, ...props }) {
  return (
    <div className={cn('rounded-xl border border-ink-100 bg-white shadow-card', className)} {...props}>
      {children}
    </div>
  );
}
