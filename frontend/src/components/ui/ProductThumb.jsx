import { useEffect, useState } from 'react';
import { Package } from 'lucide-react';
import { swatchFor, initialsFor } from '../../utils/palette';
import { cn } from '../../utils/cn';

/**
 * Standard product thumbnail with a deterministic placeholder fallback.
 */
export function ProductThumb({ name, seed, imageUrl, className, iconOnly = false }) {
  const [imageFailed, setImageFailed] = useState(false);
  const swatch = swatchFor(seed || name);

  useEffect(() => {
    setImageFailed(false);
  }, [imageUrl]);

  return (
    <div
      className={cn('flex items-center justify-center overflow-hidden rounded-lg', className)}
      style={{ background: `linear-gradient(135deg, ${swatch.from}, ${swatch.to})` }}
    >
      {!iconOnly && imageUrl && !imageFailed ? (
        <img
          src={imageUrl}
          alt={name}
          loading="lazy"
          className="h-full w-full object-cover"
          onError={() => setImageFailed(true)}
        />
      ) : iconOnly ? (
        <Package className="h-1/3 w-1/3 text-white/85" aria-hidden="true" />
      ) : (
        <span className="font-display text-2xl font-bold text-white/90">{initialsFor(name)}</span>
      )}
    </div>
  );
}
