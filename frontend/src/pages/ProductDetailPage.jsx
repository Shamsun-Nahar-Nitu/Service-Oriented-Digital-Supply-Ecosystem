import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ShoppingCart, Zap, ChevronRight, Package } from 'lucide-react';
import { productsApi } from '../api/products';
import { useFetch } from '../hooks/useFetch';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { ProductThumb } from '../components/ui/ProductThumb';
import { PriceTag } from '../components/ui/PriceTag';
import { QuantityStepper } from '../components/ui/QuantityStepper';
import { Badge } from '../components/ui/Badge';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { PRODUCT_ISSUE } from '../utils/constants';

export default function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addItem } = useCart();
  const { isAuthenticated } = useAuth();
  const toast = useToast();
  const [quantity, setQuantity] = useState(1);

  const {
    data: product,
    loading,
    error,
    refetch,
  } = useFetch(() => productsApi.retrieve(id), [id]);

  if (loading) return <PageSpinner label="Loading product…" />;
  if (error) {
    const notFound = error?.response?.status === 404;
    return (
      <ErrorState
        error={error}
        onRetry={notFound ? undefined : refetch}
        title={notFound ? 'Product not found' : "Couldn't load this product"}
        className="mx-auto my-12 max-w-lg"
      />
    );
  }
  if (!product) return null;

  const outOfStock = product.quantity_in_stock <= 0;
  const hasIssue = product.issues !== PRODUCT_ISSUE.NONE;
  const unavailable = !product.is_purchasable;

  function handleAddToCart() {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: window.location.pathname, action: 'add-to-cart' } });
      return;
    }
    addItem(product, quantity);
    toast.success(`Added ${quantity} × "${product.product_name}" to your cart.`);
  }

  function handleBuyNow() {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: window.location.pathname, action: 'buy-now' } });
      return;
    }
    addItem(product, quantity);
    navigate('/checkout');
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
      <nav aria-label="Breadcrumb" className="mb-4 flex items-center gap-1 text-sm text-ink-500">
        <Link to="/products" className="hover:text-ink-800">
          Products
        </Link>
        <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
        <Link to={`/products?category=${product.category}`} className="hover:text-ink-800">
          {product.category_name}
        </Link>
      </nav>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <div className="aspect-square w-full max-w-md">
          <ProductThumb name={product.product_name} seed={product.sku} className="h-full w-full" />
        </div>

        <div>
          {product.brand && (
            <p className="text-sm font-medium uppercase tracking-wide text-ink-400">{product.brand}</p>
          )}
          <h1 className="mt-1 font-display text-2xl font-bold text-ink-900">{product.product_name}</h1>
          <p className="mt-1 font-mono text-xs text-ink-400">SKU: {product.sku}</p>

          <div className="mt-4">
            <PriceTag
              size="lg"
              mrp={product.mrp}
              sellingPrice={product.selling_price}
              discountPercentage={product.discount_percentage}
            />
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            {unavailable ? (
              <Badge tone="danger">{outOfStock ? 'Out of stock' : 'Currently unavailable'}</Badge>
            ) : product.quantity_in_stock <= 10 ? (
              <Badge tone="gold">Only {product.quantity_in_stock} left</Badge>
            ) : (
              <Badge tone="success">In stock</Badge>
            )}
            {hasIssue && <Badge tone="danger">Flagged for review</Badge>}
          </div>

          {product.description && (
            <p className="mt-4 whitespace-pre-line text-sm leading-relaxed text-ink-600">
              {product.description}
            </p>
          )}

          <dl className="mt-4 grid grid-cols-2 gap-3 rounded-xl bg-ink-50 p-4 text-sm">
            <div>
              <dt className="text-ink-400">Sold by</dt>
              <dd className="font-medium text-ink-800">{product.vendor_name}</dd>
            </div>
            <div>
              <dt className="text-ink-400">Category</dt>
              <dd className="font-medium text-ink-800">{product.category_name}</dd>
            </div>
          </dl>

          {!unavailable && (
            <div className="mt-6 flex items-center gap-3">
              <QuantityStepper value={quantity} onChange={setQuantity} max={product.quantity_in_stock} />
              <span className="text-sm text-ink-500">{product.quantity_in_stock} available</span>
            </div>
          )}

          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={handleAddToCart}
              disabled={unavailable}
              className="flex h-11 flex-1 items-center justify-center gap-2 rounded-lg bg-ink-900 text-sm font-semibold text-white hover:bg-ink-800 disabled:pointer-events-none disabled:opacity-40"
            >
              <ShoppingCart className="h-4 w-4" aria-hidden="true" />
              Add to cart
            </button>
            <button
              type="button"
              onClick={handleBuyNow}
              disabled={unavailable}
              className="flex h-11 flex-1 items-center justify-center gap-2 rounded-lg bg-ember-500 text-sm font-semibold text-white hover:bg-ember-600 disabled:pointer-events-none disabled:opacity-40"
            >
              <Zap className="h-4 w-4" aria-hidden="true" />
              Buy now
            </button>
          </div>

          {unavailable && (
            <p className="mt-3 flex items-center gap-1.5 text-sm text-ink-500">
              <Package className="h-4 w-4" aria-hidden="true" />
              This product can&rsquo;t be purchased right now.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
