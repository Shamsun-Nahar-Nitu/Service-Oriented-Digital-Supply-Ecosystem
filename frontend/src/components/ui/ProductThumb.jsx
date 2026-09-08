import { Package } from 'lucide-react';
import { swatchFor, initialsFor } from '../../utils/palette';
import { cn } from '../../utils/cn';

/**
 * Standard product placeholder. The catalog API has no image field, so
 * every product renders a monogram tile in a color derived from its SKU —
 * consistent per product, varied across the grid, and never a random
 * gray box. See utils/palette.js for the derivation.
 */
export function ProductThumb({ name, seed, className, iconOnly = false }) {
  const swatch = swatchFor(seed || name);

  return (
    <div
      className={cn('flex items-center justify-center overflow-hidden rounded-lg', className)}
      style={{ background: `linear-gradient(135deg, ${swatch.from}, ${swatch.to})` }}
    >
      {iconOnly ? (
        <Package className="h-1/3 w-1/3 text-white/85" aria-hidden="true" />
      ) : (
        <span className="font-display text-2xl font-bold text-white/90">{initialsFor(name)}</span>
      )}
    </div>
  );
}
