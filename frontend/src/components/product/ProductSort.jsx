import { Select } from '../ui/Select';

const SORT_OPTIONS = [
  { value: '-created_date', label: 'Newest arrivals' },
  { value: 'mrp', label: 'Price: low to high' },
  { value: '-mrp', label: 'Price: high to low' },
  { value: 'product_name', label: 'Name: A to Z' },
];

/** Ordering dropdown for the product listing toolbar; maps to `?ordering=`. */
export function ProductSort({ value, onChange }) {
  return (
    <Select
      aria-label="Sort products"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      options={SORT_OPTIONS}
      className="h-9 text-sm"
    />
  );
}
