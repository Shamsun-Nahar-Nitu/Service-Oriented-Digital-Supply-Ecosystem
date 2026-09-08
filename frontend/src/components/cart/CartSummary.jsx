import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';
import { formatCurrency } from '../../utils/format';
import { pluralize } from '../../utils/format';

/** Order summary rail on the cart page — totals plus the checkout CTA. */
export function CartSummary({ itemCount, subtotal, canCheckout, blockReason }) {
  return (
    <div className="rounded-xl border border-ink-100 bg-white p-5">
      <h2 className="font-display text-base font-semibold text-ink-900">Order summary</h2>
      <dl className="mt-4 flex flex-col gap-2 text-sm">
        <div className="flex justify-between">
          <dt className="text-ink-500">{pluralize(itemCount, 'item')}</dt>
          <dd className="font-medium text-ink-900">{formatCurrency(subtotal)}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-ink-500">Shipping</dt>
          <dd className="text-ink-500">Calculated at checkout</dd>
        </div>
      </dl>
      <div className="mt-4 flex justify-between border-t border-ink-100 pt-4">
        <p className="font-display text-base font-semibold text-ink-900">Total</p>
        <p className="font-display text-lg font-bold text-ink-900">{formatCurrency(subtotal)}</p>
      </div>
      <Button as={Link} to="/checkout" fullWidth size="lg" className="mt-5" disabled={!canCheckout}>
        Proceed to checkout
      </Button>
      {!canCheckout && blockReason && (
        <p className="mt-2 text-center text-sm text-danger-600">{blockReason}</p>
      )}
    </div>
  );
}
