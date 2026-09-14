import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { XCircle } from 'lucide-react';
import { transactionsApi } from '../api/transactions';
import { paymentsApi } from '../api/payments';
import { useFetch } from '../hooks/useFetch';
import { useAsync } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PageSpinner } from '../components/ui/Spinner';
import { ErrorState } from '../components/ui/ErrorState';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Badge } from '../components/ui/Badge';
import { OrderStatusTimeline } from '../components/orders/OrderStatusTimeline';
import { PaymentPanel } from '../components/orders/PaymentPanel';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Select';
import { ConfirmDialog } from '../components/ui/ConfirmDialog';
import { formatCurrency, formatDate } from '../utils/format';
import { getErrorMessage } from '../utils/errors';
import { ORDER_STATUS_LABELS, ORDER_STATUS_SEQUENCE } from '../utils/constants';

export default function OrderDetailPage() {
  const { id } = useParams();
  const { user, isStaff, isCustomer } = useAuth();
  const toast = useToast();
  const [cancelOpen, setCancelOpen] = useState(false);
  const [nextStatus, setNextStatus] = useState('');

  const {
    data: transaction,
    loading,
    error,
    refetch,
    setData: setTransaction,
  } = useFetch(() => transactionsApi.retrieve(id), [id]);

  // No endpoint filters payments by transaction id (see
  // apps/payments/views.py — filterset_fields is ["status","method"] only),
  // so the existing payment for this order is found by scanning the
  // caller's own payments — fine at the list sizes this API returns.
  const { data: paymentsPage, setData: setPaymentsPage } = useFetch(
    () => paymentsApi.list({ page_size: 100 }),
    [id],
    { skip: !transaction }
  );
  const payment = paymentsPage?.results.find((p) => p.transaction === Number(id)) ?? null;

  const cancelAction = useAsync();
  const statusAction = useAsync();

  if (loading) return <PageSpinner label="Loading order…" />;
  if (error) {
    const notFound = error?.response?.status === 404;
    return (
      <ErrorState
        error={error}
        onRetry={notFound ? undefined : refetch}
        title={notFound ? 'Order not found' : "Couldn't load this order"}
        className="mx-auto my-12 max-w-lg"
      />
    );
  }
  if (!transaction) return null;

  const isOwner = transaction.user === user.id;
  const canCancel = transaction.status === 'PENDING' && (isOwner || isStaff);
  const onHappyPath = ORDER_STATUS_SEQUENCE.includes(transaction.status);

  function handlePaymentChange(updatedPayment) {
    setPaymentsPage((current) => ({
      ...current,
      results: current?.results.some((p) => p.id === updatedPayment.id)
        ? current.results.map((p) => (p.id === updatedPayment.id ? updatedPayment : p))
        : [...(current?.results ?? []), updatedPayment],
    }));
    refetch();
  }

  async function handleCancel() {
    try {
      const updated = await cancelAction.run(() => transactionsApi.cancel(id));
      setTransaction(updated);
      toast.success('Order cancelled.');
      setCancelOpen(false);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not cancel this order.'));
      setCancelOpen(false);
    }
  }

  async function handleStatusUpdate() {
    if (!nextStatus) return;
    try {
      const updated = await statusAction.run(() => transactionsApi.updateStatus(id, nextStatus));
      setTransaction(updated);
      toast.success(`Order marked as ${ORDER_STATUS_LABELS[nextStatus]}.`);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Could not update the order status.'));
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-xs text-ink-400">
            Order #{String(transaction.transaction_number).slice(0, 8)}
          </p>
          <h1 className="mt-1 font-display text-xl font-bold text-ink-900">
            Placed {formatDate(transaction.created_date)}
          </h1>
        </div>
        <StatusBadge status={transaction.status} className="text-sm" />
      </div>

      {onHappyPath && (
        <div className="mt-6 rounded-xl border border-ink-100 bg-white p-5">
          <OrderStatusTimeline status={transaction.status} />
        </div>
      )}

      {isStaff && (
        <div className="mt-4 flex flex-wrap items-end gap-3 rounded-xl border border-ink-100 bg-white p-4">
          <Select
            label="Update order status"
            options={Object.entries(ORDER_STATUS_LABELS).map(([value, label]) => ({ value, label }))}
            placeholder="Choose a status"
            value={nextStatus}
            onChange={(event) => setNextStatus(event.target.value)}
            className="w-56"
          />
          <Button onClick={handleStatusUpdate} loading={statusAction.loading} disabled={!nextStatus}>
            Update
          </Button>
        </div>
      )}

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
        <div className="rounded-xl border border-ink-100 bg-white p-5">
          <h2 className="font-display text-base font-semibold text-ink-900">Items</h2>
          <ul className="mt-3 divide-y divide-ink-100">
            {transaction.items.map((item) => (
              <li key={item.id} className="flex justify-between py-2.5 text-sm">
                <span className="text-ink-700">
                  {item.product_name} × {item.quantity}
                  <span className="ml-2 text-ink-400">({formatCurrency(item.unit_price)} each)</span>
                </span>
                <span className="font-medium text-ink-900">{formatCurrency(item.subtotal)}</span>
              </li>
            ))}
          </ul>
          <div className="mt-3 flex justify-between border-t border-ink-100 pt-3">
            <span className="font-display text-base font-semibold text-ink-900">Total</span>
            <span className="font-display text-lg font-bold text-ink-900">
              {formatCurrency(transaction.total_amount)}
            </span>
          </div>

          {transaction.shipping_address && (
            <div className="mt-4 border-t border-ink-100 pt-4">
              <h3 className="text-sm font-semibold text-ink-900">Shipping address</h3>
              <p className="mt-1 whitespace-pre-line text-sm text-ink-600">{transaction.shipping_address}</p>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-4">
          {(isOwner && isCustomer) || isStaff ? (
            <PaymentPanel
              transactionId={transaction.id}
              payment={payment}
              isStaff={isStaff}
              onPaymentChange={handlePaymentChange}
            />
          ) : (
            payment && (
              <div className="rounded-xl border border-ink-100 bg-white p-5">
                <h2 className="font-display text-base font-semibold text-ink-900">Payment</h2>
                <div className="mt-2">
                  <Badge tone={payment.status === 'SUCCESS' ? 'success' : payment.status === 'FAILED' ? 'danger' : 'gold'}>
                    {payment.status}
                  </Badge>
                </div>
              </div>
            )
          )}

          {canCancel && (
            <Button variant="outline" onClick={() => setCancelOpen(true)} className="text-danger-600">
              <XCircle className="h-4 w-4" aria-hidden="true" />
              Cancel order
            </Button>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={cancelOpen}
        onClose={() => setCancelOpen(false)}
        onConfirm={handleCancel}
        loading={cancelAction.loading}
        title="Cancel this order?"
        description="This can't be undone. Any reserved stock will need to be reordered separately."
        confirmLabel="Yes, cancel order"
        cancelLabel="Keep order"
      />
    </div>
  );
}
