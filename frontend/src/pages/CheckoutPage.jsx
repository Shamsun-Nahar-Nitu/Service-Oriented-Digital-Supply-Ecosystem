import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { transactionsApi } from '../api/transactions';
import { paymentsApi } from '../api/payments';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Textarea } from '../components/ui/Textarea';
import { Select } from '../components/ui/Select';
import { Button } from '../components/ui/Button';
import { pluralize } from '../utils/format';
import { getErrorMessage } from '../utils/errors';
import { PAYMENT_METHODS } from '../utils/constants';

export default function CheckoutPage() {
  const { items, itemCount, clear } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const [shippingAddress, setShippingAddress] = useState(user?.address ?? '');
  const [paymentMethod, setPaymentMethod] = useState(PAYMENT_METHODS[0].value);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (items.length === 0) {
    return <Navigate to="/cart" replace />;
  }

  const hasBlockingIssue = items.some(
    (item) => !item.product.is_purchasable || item.quantity > (item.product.quantity_in_stock ?? 0)
  );

  async function handlePlaceOrder(event) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const order = await transactionsApi.checkout({
        shipping_address: shippingAddress,
        items: items.map((item) => ({ product: item.productId, quantity: item.quantity })),
      });
      const payment = await paymentsApi.initiate({ transaction: order.id, method: paymentMethod });
      if (paymentMethod === 'ONLINE') {
        const gatewayUrl = payment.gateway_page_url ?? payment.gateway_url;
        if (!gatewayUrl) throw new Error('The payment gateway URL was not returned.');
        clear();
        window.location.assign(gatewayUrl);
        return;
      }
      clear();
      toast.success('Order placed with Cash on Delivery.');
      navigate(`/orders/${order.id}`, { replace: true });
    } catch (err) {
      setError(getErrorMessage(err, 'Could not place your order.'));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6">
      <h1 className="font-display text-xl font-bold text-ink-900">Checkout</h1>

      {hasBlockingIssue && (
        <p className="mt-4 rounded-lg bg-danger-50 px-3 py-2 text-sm text-danger-700">
          One or more items in your cart are unavailable or exceed the current stock.{' '}
          <button
            type="button"
            onClick={() => navigate('/cart')}
            className="font-medium underline underline-offset-2"
          >
            Go back to your cart
          </button>{' '}
          to fix this before placing your order.
        </p>
      )}

      <form onSubmit={handlePlaceOrder} className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <div className="rounded-xl border border-ink-100 bg-white p-5">
          <h2 className="font-display text-base font-semibold text-ink-900">Shipping address</h2>
          <Textarea
            className="mt-3"
            rows={3}
            placeholder="Street address, city, postal code"
            value={shippingAddress}
            onChange={(event) => setShippingAddress(event.target.value)}
          />

          <h2 className="mt-6 font-display text-base font-semibold text-ink-900">
            {pluralize(itemCount, 'item')}
          </h2>
          <ul className="mt-3 divide-y divide-ink-100">
            {items.map((item) => (
              <li key={item.productId} className="flex justify-between py-2 text-sm">
                <span className="text-ink-700">
                  {item.product.product_name} × {item.quantity}
                </span>
              </li>
            ))}
          </ul>
          <Select
            label="Payment method"
            value={paymentMethod}
            onChange={(event) => setPaymentMethod(event.target.value)}
            options={PAYMENT_METHODS}
            className="mt-5"
          />
        </div>

        <div className="h-fit rounded-xl border border-ink-100 bg-white p-5">
          <div className="flex justify-between pt-4">
            <span className="font-display text-base font-semibold text-ink-900">Total</span>
            <span className="font-display text-lg font-bold text-ink-900">Confirmed after order</span>
          </div>

          {error && <p className="mt-3 text-sm text-danger-600">{error}</p>}

          <Button type="submit" fullWidth size="lg" className="mt-4" loading={submitting} disabled={hasBlockingIssue}>
            {paymentMethod === 'ONLINE' ? 'Continue to Payment' : 'Place Order with Cash on Delivery'}
          </Button>
          <p className="mt-3 text-center text-xs text-ink-400">The backend confirms your final payment amount.</p>
        </div>
      </form>
    </div>
  );
}
