import { formatCurrency, formatDiscount } from '../../utils/format';
import { cn } from '../../utils/cn';

/**
 * Renders a product's selling price, with the struck-through MRP and a
 * discount badge when the product actually has a discount — several
 * seeded products have discount_percentage = 0, where showing a crossed
 * out identical MRP would just be visual noise.
 */
export function PriceTag({ mrp, sellingPrice, discountPercentage, size = 'md', className }) {
  const discountLabel = formatDiscount(discountPercentage);
  const hasDiscount = Boolean(discountLabel) && Number(sellingPrice) < Number(mrp);

  const priceSize = size === 'lg' ? 'text-2xl' : size === 'sm' ? 'text-sm' : 'text-base';

  return (
    <div className={cn('flex flex-wrap items-baseline gap-2', className)}>
      <span className={cn('font-display font-bold text-ink-900', priceSize)}>
        {formatCurrency(sellingPrice)}
      </span>
      {hasDiscount && (
        <>
          <span className="text-sm text-ink-400 line-through">{formatCurrency(mrp)}</span>
          <span className="text-sm font-semibold text-success-600">{discountLabel}</span>
        </>
      )}
    </div>
  );
}
