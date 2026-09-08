/**
 * Deterministic accent color for product thumbnails.
 *
 * The catalog API has no image field (see apps/products/models.py), so
 * every product needs a placeholder. Rather than one flat gray box for the
 * whole catalog, each product gets a stable color drawn from a small curated
 * set, keyed off its SKU — the same product always renders the same color,
 * different products fan out across the palette, and nothing here depends
 * on random values that would repaint on every render.
 */
const SWATCHES = [
  { from: '#1F2645', to: '#404B73' }, // ink
  { from: '#FF5A1F', to: '#FF9E6B' }, // ember
  { from: '#B45400', to: '#FFB020' }, // gold
  { from: '#0B6650', to: '#1AA179' }, // success
  { from: '#7E220F', to: '#C42E05' }, // deep ember
  { from: '#2C3559', to: '#8D97B6' }, // slate
];

function hashString(value) {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

export function swatchFor(seed) {
  const key = String(seed || 'product');
  return SWATCHES[hashString(key) % SWATCHES.length];
}

/** First letters of up to two words, for the placeholder monogram. */
export function initialsFor(name) {
  if (!name) return '?';
  const words = name.trim().split(/\s+/).slice(0, 2);
  return words.map((word) => word[0]?.toUpperCase() ?? '').join('');
}
