const STORAGE_KEY = 'shopnest.pendingCartIntent';

/**
 * When a guest clicks "Add to cart" or "Buy now", ProductCard/
 * ProductDetailPage redirect them to /login before the item is ever added
 * — there's nothing to restore otherwise, since CartContext's addItem was
 * never called. This is where that interrupted intent is parked so
 * LoginPage can finish the job once they're signed in: add the product for
 * real, then send them to /cart (or straight to /checkout for "buy now")
 * instead of wherever they'd otherwise land after logging in.
 *
 * sessionStorage, not localStorage — this should never survive longer than
 * one login flow, let alone across browser sessions.
 */
export function savePendingCartIntent(product, quantity, action) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ product, quantity, action }));
  } catch {
    // Storage can throw in private-browsing/locked-down contexts. Worst
    // case, the user just has to click "Add to cart" again after login.
  }
}

/** Reads and clears the pending intent in one step — it's meant to be
 * consumed exactly once, right after a successful login. */
export function takePendingCartIntent() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    sessionStorage.removeItem(STORAGE_KEY);
    return JSON.parse(raw);
  } catch {
    return null;
  }
}