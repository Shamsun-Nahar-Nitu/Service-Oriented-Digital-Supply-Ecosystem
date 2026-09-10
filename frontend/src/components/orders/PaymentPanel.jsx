import { useState } from 'react';
import { ShieldAlert } from 'lucide-react';
import { Button } from '../ui/Button';
import { Select } from '../ui/Select';
import { Badge } from '../ui/Badge';
import { paymentsApi } from '../../api/payments';
import { useAsync } from '../../hooks/useAsync';
import { getErrorMessage } from '../../utils/errors';
import { formatCurrency, formatDateTime } from '../../utils/format';
import { PAYMENT_METHODS } from '../../utils/constants';

export function PaymentPanel({ transactionId, payment }) {
  const [method, setMethod] = useState(PAYMENT_METHODS[0].value);
  const { run, loading, error } = useAsync();

  async function handleInitiate() {
    try {
      const created = await run(() => paymentsApi.initiate({ transaction: transactionId, method }));
      if (!created.gateway_url) throw new Error('The payment gateway URL was not returned.');
      window.location.href = created.gateway_url;
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
          You will be redirected to the secure payment gateway.
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
