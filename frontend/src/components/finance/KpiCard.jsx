import { Card } from '../ui/Card';
import { cn } from '../../utils/cn';

/** One metric tile — "Gross revenue", "৳12,400", optional trailing hint. */
export function KpiCard({ label, value, hint, className }) {
  return (
    <Card className={cn('p-4', className)}>
      <p className="text-xs font-medium uppercase tracking-wide text-ink-500">{label}</p>
      <p className="mt-1.5 text-2xl font-bold text-ink-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-ink-500">{hint}</p>}
    </Card>
  );
}

/** Responsive grid all three dashboards lay their KpiCards into. */
export function KpiGrid({ children }) {
  return <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">{children}</div>;
}