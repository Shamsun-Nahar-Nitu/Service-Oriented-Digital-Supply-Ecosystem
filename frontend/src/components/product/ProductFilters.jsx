import { Select } from '../ui/Select';
import { Input } from '../ui/Input';
import { Checkbox } from '../ui/Checkbox';
import { Button } from '../ui/Button';

/**
 * Sidebar filter panel for the product listing page. Purely controlled —
 * ProductsPage owns the actual filter state (synced to the URL) and passes
 * values + a single onChange(patch) down, so the URL stays the source of
 * truth and filters survive a page refresh or a shared link.
 */
export function ProductFilters({ categories, categoriesLoading, values, onChange, onClear }) {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-ink-900">Filters</h2>
        <Button variant="link" size="sm" onClick={onClear}>
          Clear all
        </Button>
      </div>

      <Select
        label="Category"
        placeholder="All categories"
        value={values.category}
        onChange={(event) => onChange({ category: event.target.value })}
        options={categories.map((category) => ({ value: String(category.id), label: category.name }))}
        disabled={categoriesLoading}
      />

      <fieldset className="flex flex-col gap-2">
        <legend className="text-sm font-medium text-ink-800">Price range</legend>
        <div className="flex items-center gap-2">
          <Input
            type="number"
            min="0"
            aria-label="Minimum price"
            placeholder="Min"
            value={values.minPrice}
            onChange={(event) => onChange({ minPrice: event.target.value })}
          />
          <span className="text-ink-400">–</span>
          <Input
            type="number"
            min="0"
            aria-label="Maximum price"
            placeholder="Max"
            value={values.maxPrice}
            onChange={(event) => onChange({ maxPrice: event.target.value })}
          />
        </div>
      </fieldset>

      <Checkbox
        label="In stock only"
        checked={values.inStock}
        onChange={(event) => onChange({ inStock: event.target.checked })}
      />
    </div>
  );
}
