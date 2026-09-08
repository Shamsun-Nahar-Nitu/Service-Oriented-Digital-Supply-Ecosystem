import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag } from 'lucide-react';
import { productsApi } from '../api/products';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { CartItem } from '../components/cart/CartItem';
import { CartSummary } from '../components/cart/CartSummary';
import { EmptyState } from '../components/ui/EmptyState';
import { Button } from '../components/ui/Button';
import { Spinner } from '../components/ui/Spinner';

/**
 * The cart only ever holds a snapshot taken when an item was added, which
 * can drift from reality (price changed, stock sold out, product
 * deactivated) by the time someone checks out. On mount, this page
 * re-fetches every line item against the live API — removing products that
 * no longer exist and refreshing price/stock for the rest — so CartItem's
 * warnings are always based on current data, not what was true minutes ago.
 */
export default function CartPage() {
  const { items, itemCount, subtotal, syncProduct, removeItem } = useCart();
  const toast = useToast();
  const [syncing, setSyncing] = useState(true);
  const hasSynced = useRef(false);

  useEffect(() => {
    if (hasSynced.current || items.length === 0) {
      setSyncing(false);
      return;
    }
    hasSynced.current = true;

    let cancelled = false;
    async function sync() {
      const results = await Promise.allSettled(
        items.map((item) => productsApi.retrieve(item.productId))
      );
      if (cancelled) return;

      let removedAny = false;
      results.forEach((result, index) => {
        const { productId } = items[index];
        if (result.status === 'fulfilled') {
          syncProduct(result.value);
        } else if (result.reason?.response?.status === 404) {
          removeItem(productId);
          removedAny = true;
        }
      });
      if (removedAny) {
        toast.info('Some items in your cart are no longer available and were removed.');
      }
      setSyncing(false);
    }
    sync();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16">
        <EmptyState
          icon={ShoppingBag}
          title="Your cart is empty"
          description="Browse the catalog and add something you like."
          action={
            <Button as={Link} to="/products">
              Start shopping
            </Button>
          }
        />
      </div>
    );
  }

  const hasBlockingIssue = items.some(
    (item) => !item.product.is_purchasable || item.quantity > (item.product.quantity_in_stock ?? 0)
  );

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
      <h1 className="font-display text-xl font-bold text-ink-900">Your cart</h1>

      {syncing ? (
        <div className="mt-6 flex items-center gap-2 text-sm text-ink-500">
          <Spinner size={16} /> Checking current prices and stock…
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
          <div className="rounded-xl border border-ink-100 bg-white px-4">
            {items.map((item) => (
              <CartItem key={item.productId} item={item} />
            ))}
          </div>
          <CartSummary
            itemCount={itemCount}
            subtotal={subtotal}
            canCheckout={!hasBlockingIssue}
            blockReason="Resolve the flagged items above before checking out."
          />
        </div>
      )}
    </div>
  );
}
