import { useState } from 'react';
import { CheckCircle2, XCircle, ShieldAlert } from 'lucide-react';
import { Button } from '../ui/Button';
import { Select } from '../ui/Select';
import { Badge } from '../ui/Badge';
import { paymentsApi } from '../../api/payments';
import { useAsync } from '../../hooks/useAsync';
import { useToast } from '../../context/ToastContext';
import { getErrorMessage } from '../../utils/errors';
import { formatCurrency, formatDateTime } from '../../utils/format';
import { PAYMENT_METHODS } from '../../utils/constants';

/**
 * There's no real payment gateway behind this API — `confirm` simulates the
 * webhook a provider like Stripe would send (see
 * apps/payments/views.py::PaymentViewSet.confirm). This panel makes that
 * explicit rather than pretending it's a real charge, and lets a person
 * step through initiate → confirm exactly as the API models it.
 */
export function PaymentPanel({ transactionId, payment, onPaymentChange }) {
  const [method, setMethod] = useState(PAYMENT_METHODS[0].value);
  const { run, loading, error } = useAsync();
  const toast = useToast();

  async function handleInitiate() {
    try {
      const created = await run(() => paymentsApi.initiate({ transaction: transactionId, method }));
      onPaymentChange(created);
    } catch {
      // Error surfaced inline below via `error`.
    }
  }

  async function handleConfirm(success) {
    try {
      const updated = await run(() => paymentsApi.confirm(payment.id, { success }));
      onPaymentChange(updated);
      toast[success ? 'success' : 'error'](
        success ? 'Payment confirmed.' : 'Payment marked as failed.'
      );
    } catch {
      // Error surfaced inline below via `error`.
    }
  }

  if (!payment) {
    return (
      <div className="rounded-xl border border-ink-100 bg-white p-5">
        <h2 className="font-display text-base font-semibold text-ink-900">Payment</h2>
        <p className="mt-1 flex items-center gap-1.5 text-xs text-ink-400">
          <ShieldAlert className="h-3.5 w-3.5" aria-hidden="true" />
          Demo checkout — no real charge is made.
        </p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end">
          <Select
            label="Payment method"
            value={method}
            onChange={(event) => setMethod(event.target.value)}
            options={PAYMENT_METHODS}
            className="sm:w-56"
          />
          <Button onClick={handleInitiate} loading={loading}>
            Pay now
          </Button>
        </div>
        {error && <p className="mt-2 text-sm text-danger-600">{getErrorMessage(error)}</p>}
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-ink-100 bg-white p-5">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-base font-semibold text-ink-900">Payment</h2>
        <PaymentStatusBadge status={payment.status} />
      </div>

      <dl className="mt-3 flex flex-col gap-1.5 text-sm">
        <Row label="Method" value={PAYMENT_METHODS.find((m) => m.value === payment.method)?.label} />
        <Row label="Amount" value={formatCurrency(payment.amount)} />
        {payment.gateway_reference && <Row label="Reference" value={payment.gateway_reference} />}
        {payment.paid_at && <Row label="Paid at" value={formatDateTime(payment.paid_at)} />}
      </dl>

      {payment.status === 'PENDING' && (
        <div className="mt-4 flex flex-wrap gap-2 border-t border-ink-100 pt-4">
          <Button size="sm" onClick={() => handleConfirm(true)} loading={loading}>
            <CheckCircle2 className="h-4 w-4" aria-hidden="true" /> Confirm payment
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleConfirm(false)} loading={loading}>
            <XCircle className="h-4 w-4" aria-hidden="true" /> Simulate failure
          </Button>
        </div>
      )}

      {payment.status === 'FAILED' && (
        <div className="mt-4 border-t border-ink-100 pt-4">
          <Button size="sm" onClick={() => handleConfirm(true)} loading={loading}>
            Retry payment
          </Button>
        </div>
      )}

      {error && <p className="mt-2 text-sm text-danger-600">{getErrorMessage(error)}</p>}
    </div>
  );
}

function Row({ label, value }) {
  if (!value) return null;
  return (
    <div className="flex justify-between">
      <dt className="text-ink-500">{label}</dt>
      <dd className="font-medium text-ink-900">{value}</dd>
    </div>
  );
}

function PaymentStatusBadge({ status }) {
  const tone = { SUCCESS: 'success', FAILED: 'danger', PENDING: 'gold', REFUNDED: 'neutral' }[status];
  return <Badge tone={tone}>{status[0] + status.slice(1).toLowerCase()}</Badge>;
}
