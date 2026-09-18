import { Select } from '../ui/Select';

const PERIOD_OPTIONS = [
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 90 days' },
  { value: '12m', label: 'Last 12 months' },
  { value: 'this_month', label: 'This month' },
  { value: 'last_month', label: 'Last month' },
  { value: 'all', label: 'All time' },
];

/** Bound to `?period=` in the URL, the same pattern AdminOrdersPage uses
 * for its status filter — so the chosen range survives a refresh and is
 * shareable as a link. */
export function PeriodSelect({ value, onChange }) {
  return (
    <Select
      aria-label="Date range"
      options={PERIOD_OPTIONS}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="w-40"
    />
  );
}

export const DEFAULT_PERIOD = '30d';