import { CheckCircle2, Download, XCircle } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { ErrorState } from '../components/ui/ErrorState';
import { PageSpinner } from '../components/ui/Spinner';
import { StatusBadge } from '../components/ui/StatusBadge';
import { paymentsApi } from '../api/payments';
import { transactionsApi } from '../api/transactions';
import { useFetch } from '../hooks/useFetch';
import { useAsync } from '../hooks/useAsync';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../utils/errors';
import { formatCurrency, formatDate } from '../utils/format';

const KIND_CONTENT = {
  success: {
    icon: CheckCircle2,
    iconClass: 'text-success-500',
    title: 'Payment successful!',
    message: "Thanks for your order — we've got it and you're all set.",
  },
  fail: {
    icon: XCircle,
    iconClass: 'text-danger-500',
    title: "Payment didn't go through",
    message: 'No charge went through on our end. Please try again, or use a different payment method.',
  },
  cancel: {
    icon: XCircle,
    iconClass: 'text-ink-400',
    title: 'Payment cancelled',
    message: 'You cancelled before finishing payment — nothing was charged. You can pick up where you left off any time.',
  },
};

/** Shared by /payment/success, /payment/fail and /payment/cancel (see
 * PaymentSuccessPage/PaymentFailPage/PaymentCancelPage). Rendered inside
 * MainLayout, same as every other page — with the normal header showing,
 * a signed-in customer can see at a glance that they're still signed in
 * once the SSLCOMMERZ round trip lands them back here. */
export function PaymentResultPage({ kind }) {
  const toast = useToast();
  const [searchParams] = useSearchParams();
  const paymentId = searchParams.get('payment_id') || searchParams.get('payment');
  const transactionReference = searchParams.get('tran_id');

  const { data: payment, loading: paymentLoading } = useFetch(
    async () => {
      if (paymentId) return paymentsApi.retrieve(paymentId);
      const page = await paymentsApi.list({ page_size: 100 });
      return page?.results?.find(
        (item) => item.gateway_transaction_id === transactionReference || item.gateway_reference === transactionReference
      );
    },
    [paymentId, transactionReference],
    { skip: !paymentId && !transactionReference }
  );

  const { data: order, loading: orderLoading } = useFetch(
    () => transactionsApi.retrieve(payment.transaction),
    [payment?.transaction],
    { skip: !payment?.transaction }
  );

  const retryAction = useAsync();
  const receiptAction = useAsync();

  const content = KIND_CONTENT[kind];
  const Icon = content.icon;
  const loading = paymentLoading || (Boolean(payment?.transaction) && orderLoading);
  const orderLink = payment?.transaction ? `/orders/${payment.transaction}` : '/orders';
  const orderRef = order ? String(order.transaction_number).slice(0, 8) : null;

  // A cancelled online payment reaches the exact same FAILED status a
  // declined one does (see SSLCommerzCallbackView — both callback types
  // call mark_failed()), so retry is offered on both pages, not just
  // /payment/fail.
  const canRetry = payment?.status === 'FAILED' && payment?.method === 'ONLINE';

  async function handleRetry() {
    try {
      const updated = await retryAction.run(() => paymentsApi.retry(payment.id));
      const gatewayUrl = updated.gateway_page_url ?? updated.gateway_url;
      if (!gatewayUrl) throw new Error('The payment gateway URL was not returned.');
      window.location.assign(gatewayUrl);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not start a new payment attempt.'));
    }
  }

  async function handleDownloadReceipt() {
    try {
      await receiptAction.run(() => paymentsApi.downloadReceipt(payment.id, orderRef));
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not generate the receipt.'));
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-16 text-center sm:px-6">
      <Icon className={`mx-auto h-14 w-14 ${content.iconClass}`} aria-hidden="true" />
      <h1 className="mt-4 font-display text-2xl font-bold text-ink-900">{content.title}</h1>
      <p className="mt-2 text-sm text-ink-600">{content.message}</p>

      {loading && <PageSpinner label="Loading your order…" />}

      {!loading && !payment && (paymentId || transactionReference) && (
        <ErrorState title="Couldn't find this payment" className="mt-6" />
      )}

      {!loading && payment && (
        <div className="mt-6 rounded-xl border border-ink-100 bg-white text-left">
          <div className="flex items-center justify-between border-b border-ink-100 p-5">
            <div>
              {orderRef && <p className="font-mono text-xs text-ink-400">Order #{orderRef}</p>}
              <p className="mt-0.5 text-lg font-bold text-ink-900">{formatCurrency(payment.amount)}</p>
            </div>
            <StatusBadge status={payment.status} kind="payment" />
          </div>

          {kind === 'success' && order && (
            <div className="p-5">
              <ul className="divide-y divide-ink-100">
                {order.items.map((item) => (
                  <li key={item.id} className="flex justify-between py-2 text-sm">
                    <span className="text-ink-700">
                      {item.product_name} × {item.quantity}
                    </span>
                    <span className="font-medium text-ink-900">{formatCurrency(item.subtotal)}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-3 space-y-1 border-t border-ink-100 pt-3 text-sm">
                <div className="flex justify-between text-ink-500">
                  <span>Items subtotal</span>
                  <span>{formatCurrency(order.items_subtotal)}</span>
                </div>
                <div className="flex justify-between text-ink-500">
                  <span>Platform service fee</span>
                  <span>{formatCurrency(order.platform_fee)}</span>
                </div>
                <div className="flex justify-between pt-1 text-base font-bold text-ink-900">
                  <span>Total paid</span>
                  <span>{formatCurrency(order.total_amount)}</span>
                </div>
              </div>
              <p className="mt-3 text-xs text-ink-400">
                Paid via {payment.method === 'ONLINE' ? 'online payment' : 'Cash on Delivery'}
                {payment.paid_at && <> · {formatDate(payment.paid_at)}</>}
              </p>

              <Button
                variant="secondary"
                onClick={handleDownloadReceipt}
                loading={receiptAction.loading}
                className="mt-4 w-full justify-center"
              >
                <Download className="h-4 w-4" aria-hidden="true" />
                Download receipt
              </Button>
            </div>
          )}

          {kind !== 'success' && (
            <div className="p-5">
              {canRetry ? (
                <Button onClick={handleRetry} loading={retryAction.loading} className="w-full justify-center">
                  Try again
                </Button>
              ) : (
                <p className="text-sm text-ink-500">
                  {payment.method === 'COD'
                    ? 'This order is Cash on Delivery — nothing further is needed here.'
                    : "This payment can't be retried from here — check the order for what to do next."}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Button as={Link} to={orderLink} variant="secondary">View order</Button>
        <Link to="/products" className="rounded-lg border border-ink-200 px-4 py-2 text-sm font-semibold text-ink-700">
          Continue shopping
        </Link>
        <Link to="/" className="rounded-lg px-4 py-2 text-sm font-semibold text-ink-500 hover:text-ink-700">
          Back to home
        </Link>
      </div>
    </div>
  );
}