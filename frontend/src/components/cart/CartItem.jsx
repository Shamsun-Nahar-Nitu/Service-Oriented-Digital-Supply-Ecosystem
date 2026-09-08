import { Link } from 'react-router-dom';
import { Trash2, AlertTriangle } from 'lucide-react';
import { ProductThumb } from '../ui/ProductThumb';
import { QuantityStepper } from '../ui/QuantityStepper';
import { formatCurrency } from '../../utils/format';
import { useCart } from '../../context/CartContext';

/**
 * A single cart line. `product` is the (possibly stale) snapshot taken
 * when the item was added; CartPage refreshes it against the live API on
 * mount via `syncProduct`, so this component always renders whatever the
 * freshest known data is and flags it when that data says the item can no
 * longer be fulfilled as requested.
 */
export function CartItem({ item }) {
  const { setQuantity, removeItem } = useCart();
  const { product, quantity } = item;

  const stock = product.quantity_in_stock ?? 0;
  const unavailable = !product.is_purchasable;
  const exceedsStock = !unavailable && quantity > stock;

  return (
    <div className="flex gap-4 border-b border-ink-100 py-4 last:border-b-0">
      <Link to={`/products/${product.id}`} className="shrink-0">
        <ProductThumb name={product.product_name} seed={product.sku} className="h-20 w-20" />
      </Link>

      <div className="flex flex-1 flex-col gap-1">
        <Link
          to={`/products/${product.id}`}
          className="text-sm font-medium text-ink-900 hover:text-ember-600"
        >
          {product.product_name}
        </Link>
        <p className="text-sm text-ink-500">{formatCurrency(product.selling_price)} each</p>

        {unavailable && (
          <p className="flex items-center gap-1 text-sm font-medium text-danger-600">
            <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
            No longer available — remove to continue checkout.
          </p>
        )}
        {exceedsStock && (
          <p className="flex items-center gap-1 text-sm font-medium text-gold-700">
            <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
            Only {stock} left in stock. Reduce quantity to continue.
          </p>
        )}

        <div className="mt-2 flex items-center justify-between gap-3">
          <QuantityStepper
            value={quantity}
            onChange={(next) => setQuantity(product.id, next)}
            max={Math.max(stock, 0)}
            disabled={unavailable}
          />
          <button
            type="button"
            onClick={() => removeItem(product.id)}
            className="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-sm font-medium text-ink-500 hover:bg-danger-50 hover:text-danger-600"
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
            Remove
          </button>
        </div>
      </div>

      <p className="shrink-0 font-display text-sm font-semibold text-ink-900">
        {formatCurrency(Number(product.selling_price) * quantity)}
      </p>
    </div>
  );
}
