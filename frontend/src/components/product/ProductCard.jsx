import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart } from 'lucide-react';
import { ProductThumb } from '../ui/ProductThumb';
import { PriceTag } from '../ui/PriceTag';
import { Badge } from '../ui/Badge';
import { useCart } from '../../context/CartContext';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { savePendingCartIntent } from '../../utils/pendingCartIntent';

/**
 * Standard catalog tile, used on the home page, product listing, and any
 * "related products" rail. Owns its own "add to cart" action so grids don't
 * need to wire that up per usage.
 */
export function ProductCard({ product }) {
  const { addItem } = useCart();
  const { isAuthenticated } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const outOfStock = product.quantity_in_stock <= 0;
  const unavailable = !product.is_purchasable;

  function handleAddToCart(event) {
    event.preventDefault();
    event.stopPropagation();
    if (!isAuthenticated) {
      savePendingCartIntent(product, 1, 'add-to-cart');
      navigate('/login', { state: { from: '/cart' } });
      return;
    }
    addItem(product, 1);
    toast.success(`Added "${product.product_name}" to your cart.`);
  }

  return (
    <Link
      to={`/products/${product.id}`}
      className="group flex flex-col overflow-hidden rounded-xl border border-ink-100 bg-white transition-shadow hover:shadow-raised"
    >
      <div className="relative aspect-square w-full overflow-hidden">
        <ProductThumb
          name={product.product_name}
          seed={product.sku}
          imageUrl={product.image_url}
          className="h-full w-full"
        />
        {product.discount_percentage > 0 && (
          <Badge tone="ember" className="absolute left-2 top-2">
            -{Number(product.discount_percentage)}%
          </Badge>
        )}
        {unavailable && (
          <div className="absolute inset-0 flex items-center justify-center bg-ink-950/50">
            <Badge tone="danger">{outOfStock ? 'Out of stock' : 'Unavailable'}</Badge>
          </div>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-1.5 p-3">
        {product.brand && (
          <p className="truncate text-xs font-medium uppercase tracking-wide text-ink-400">
            {product.brand}
          </p>
        )}
        <h3 className="line-clamp-2 text-sm font-medium text-ink-900 group-hover:text-ember-600">
          {product.product_name}
        </h3>
        <div className="mt-auto pt-1">
          <PriceTag
            mrp={product.mrp}
            sellingPrice={product.selling_price}
            discountPercentage={product.discount_percentage}
          />
        </div>
        <button
          type="button"
          onClick={handleAddToCart}
          disabled={unavailable}
          className="mt-2 flex h-9 items-center justify-center gap-1.5 rounded-lg bg-ink-900 text-sm font-medium text-white transition-colors hover:bg-ember-600 disabled:pointer-events-none disabled:opacity-40"
        >
          <ShoppingCart className="h-4 w-4" aria-hidden="true" />
          Add to cart
        </button>
      </div>
    </Link>
  );
}