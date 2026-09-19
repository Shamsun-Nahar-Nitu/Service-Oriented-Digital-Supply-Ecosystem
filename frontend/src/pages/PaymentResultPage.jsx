import { Link, useSearchParams } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { ErrorState } from '../components/ui/ErrorState';
import { PageSpinner } from '../components/ui/Spinner';
import { paymentsApi } from '../api/payments';
import { useFetch } from '../hooks/useFetch';
import { useAsync } from '../hooks/useAsync';
import { getErrorMessage } from '../utils/errors';
import { formatCurrency } from '../utils/format';
import { StatusBadge } from '../components/ui/StatusBadge';

export function PaymentResultPage({ kind }) {
  const [searchParams] = useSearchParams();
  const paymentId = searchParams.get('payment_id') || searchParams.get('payment');
  const transactionReference = searchParams.get('tran_id');
  const { data: payment, loading } = useFetch(
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
  const retryAction = useAsync();

  const content = {
    success: { title: 'Payment status', message: 'The backend payment status is the source of truth.' },
    fail: { title: 'Payment failed', message: 'The backend payment status is the source of truth.' },
    cancel: { title: 'Payment was cancelled', message: 'You can return to the order and try again.' },
  }[kind];

  async function handleRetry() {
    try {
      const updated = await retryAction.run(() => paymentsApi.retry(payment.id));
      const gatewayUrl = updated.gateway_page_url ?? updated.gateway_url;
      if (!gatewayUrl) throw new Error('The payment gateway URL was not returned.');
      window.location.assign(gatewayUrl);
    } catch {
      // Error is surfaced inline below via retryAction.error.
    }
  }

  const orderLink = payment?.transaction ? `/orders/${payment.transaction}` : '/orders';

  return (
    <div className="mx-auto max-w-lg px-4 py-16 text-center sm:px-6">
      <h1 className="font-display text-2xl font-bold text-ink-900">{content.title}</h1>
      <p className="mt-2 text-sm text-ink-600">{content.message}</p>
      {loading && <PageSpinner label="Checking payment status…" />}
      {!loading && !payment && (paymentId || transactionReference) && (
        <ErrorState title="Couldn’t find this payment" className="mt-6" />
      )}
      {payment && (
        <div className="mt-6 rounded-xl border border-ink-100 bg-white p-5">
          <p className="text-sm text-ink-500">{formatCurrency(payment.amount)}</p>
          <StatusBadge status={payment.status} kind="payment" className="mt-2" />
          {kind === 'success' && payment.status !== 'SUCCESS' && (
            <p className="mt-3 text-sm text-ink-600">Payment received. We&apos;re confirming your transaction.</p>
          )}
          {kind === 'fail' && payment.status === 'FAILED' && payment.method === 'ONLINE' && (
            <Button onClick={handleRetry} loading={retryAction.loading} className="mt-4">
              Try Again
            </Button>
          )}
          {retryAction.error && (
            <p className="mt-2 text-sm text-danger-600">{getErrorMessage(retryAction.error)}</p>
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