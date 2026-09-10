import { Link, useSearchParams } from 'react-router-dom';
import { Badge } from '../components/ui/Badge';
import { PageSpinner } from '../components/ui/Spinner';
import { paymentsApi } from '../api/payments';
import { useFetch } from '../hooks/useFetch';

export function PaymentResultPage({ kind }) {
  const [searchParams] = useSearchParams();
  const paymentId = searchParams.get('payment_id') || searchParams.get('payment');
  const { data: payment, loading } = useFetch(
    () => paymentsApi.retrieve(paymentId),
    [paymentId],
    { skip: !paymentId }
  );

  const content = {
    success: { title: 'Payment return received', message: 'The backend will confirm the final payment status.' },
    fail: { title: 'Payment was not completed', message: 'The backend payment status is the source of truth.' },
    cancel: { title: 'Payment was cancelled', message: 'You can return to the order and try again.' },
  }[kind];

  return (
    <div className="mx-auto max-w-lg px-4 py-16 text-center sm:px-6">
      <h1 className="font-display text-2xl font-bold text-ink-900">{content.title}</h1>
      <p className="mt-2 text-sm text-ink-600">{content.message}</p>
      {loading && <PageSpinner label="Checking payment status…" />}
      {payment && (
        <div className="mt-6 rounded-xl border border-ink-100 bg-white p-5">
          <p className="text-sm text-ink-500">Backend payment status</p>
          <Badge tone={payment.status === 'SUCCESS' ? 'success' : payment.status === 'FAILED' ? 'danger' : 'gold'} className="mt-2">
            {payment.status}
          </Badge>
        </div>
      )}
      <div className="mt-8 flex justify-center gap-3">
        <Link to="/orders" className="rounded-lg bg-ink-900 px-4 py-2 text-sm font-semibold text-white">
          View orders
        </Link>
        <Link to="/products" className="rounded-lg border border-ink-200 px-4 py-2 text-sm font-semibold text-ink-700">
          Continue shopping
        </Link>
      </div>
    </div>
  );
}
