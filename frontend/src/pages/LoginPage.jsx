import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LoginForm } from '../components/forms/LoginForm';
import { getHomePath } from '../utils/roleHome';
import { ROLES } from '../utils/constants';
import { useCart } from '../context/CartContext';
import { useToast } from '../context/ToastContext';
import { takePendingCartIntent } from '../utils/pendingCartIntent';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const cart = useCart();
  const toast = useToast();
  const from = location.state?.from;

  function handleSuccess(user) {
    // A guest clicking "Add to cart" or "Buy now" gets sent here before the
    // item is ever added (see ProductCard/ProductDetailPage) — finish that
    // now, in preference to wherever they'd otherwise land, so the product
    // is actually in the cart they're about to see.
    const intent = takePendingCartIntent();
    if (intent?.product && user.role === ROLES.CUSTOMER) {
      cart.addItem(intent.product, intent.quantity || 1);
      toast.success(`Added ${intent.quantity || 1} × "${intent.product.product_name}" to your cart.`);
      navigate(intent.action === 'buy-now' ? '/checkout' : '/cart', { replace: true });
      return;
    }

    const destination = typeof from === 'string' ? from : from?.pathname;
    navigate(destination || getHomePath(user.role), { replace: true });
  }

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-ink-900">Welcome back</h1>
      <p className="mt-1 text-sm text-ink-500">Log in to continue.</p>

      <div className="mt-6">
        <LoginForm onSuccess={handleSuccess} />
      </div>

      <p className="mt-6 text-center text-sm text-ink-500">
        New here?{' '}
        <Link to="/register" className="font-medium text-ember-600 hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}