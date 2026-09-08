import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { CART_STORAGE_KEY } from '../utils/constants';

const CartContext = createContext(null);

/**
 * The backend has no cart model — checkout accepts a raw list of
 * `{product, quantity}` (see apps/transactions/serializers.py::CheckoutSerializer)
 * and expects the frontend to have assembled it. So the cart lives entirely
 * client-side, persisted to localStorage, and only touches the API at the
 * moment of checkout.
 *
 * Each entry stores a snapshot of the product alongside the quantity so the
 * cart can render without a network round trip; CartPage re-fetches the
 * live product on mount to catch price/stock drift before checkout.
 */
function readInitialState() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function CartProvider({ children }) {
  const [items, setItems] = useState(readInitialState);

  useEffect(() => {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
  }, [items]);

  const addItem = useCallback((product, quantity = 1) => {
    setItems((current) => {
      const existing = current.find((item) => item.productId === product.id);
      if (existing) {
        return current.map((item) =>
          item.productId === product.id
            ? { ...item, quantity: item.quantity + quantity, product }
            : item
        );
      }
      return [...current, { productId: product.id, quantity, product }];
    });
  }, []);

  const removeItem = useCallback((productId) => {
    setItems((current) => current.filter((item) => item.productId !== productId));
  }, []);

  const setQuantity = useCallback((productId, quantity) => {
    setItems((current) => {
      if (quantity <= 0) {
        return current.filter((item) => item.productId !== productId);
      }
      return current.map((item) => (item.productId === productId ? { ...item, quantity } : item));
    });
  }, []);

  /** Merges fresh product data (price/stock) into cart snapshots without changing quantities. */
  const syncProduct = useCallback((product) => {
    setItems((current) =>
      current.map((item) => (item.productId === product.id ? { ...item, product } : item))
    );
  }, []);

  const clear = useCallback(() => setItems([]), []);

  const value = useMemo(() => {
    const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
    const subtotal = items.reduce(
      (sum, item) => sum + Number(item.product.selling_price) * item.quantity,
      0
    );
    return { items, itemCount, subtotal, addItem, removeItem, setQuantity, syncProduct, clear };
  }, [items, addItem, removeItem, setQuantity, syncProduct, clear]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider.');
  }
  return context;
}
