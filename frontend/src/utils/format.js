const CURRENCY_CODE = import.meta.env.VITE_CURRENCY_CODE || 'BDT';
const CURRENCY_LOCALE = import.meta.env.VITE_CURRENCY_LOCALE || 'en-BD';

const currencyFormatter = new Intl.NumberFormat(CURRENCY_LOCALE, {
  style: 'currency',
  currency: CURRENCY_CODE,
  currencyDisplay: 'symbol',
  maximumFractionDigits: 2,
});

const dateFormatter = new Intl.DateTimeFormat(CURRENCY_LOCALE, {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
});

const dateTimeFormatter = new Intl.DateTimeFormat(CURRENCY_LOCALE, {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
});

/** Formats a decimal string/number from the API into a localized currency string. */
export function formatCurrency(value) {
  const number = Number(value);
  if (Number.isNaN(number)) return currencyFormatter.format(0);
  return currencyFormatter.format(number);
}

/** Formats an ISO date/datetime string into "4 Sep 2026". */
export function formatDate(isoString) {
  if (!isoString) return '—';
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return '—';
  return dateFormatter.format(date);
}

/** Formats an ISO datetime string into "4 Sep 2026, 3:45 PM". */
export function formatDateTime(isoString) {
  if (!isoString) return '—';
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return '—';
  return dateTimeFormatter.format(date);
}

/** Formats a 0-100 discount value as "10% off". Returns null when there's no discount. */
export function formatDiscount(discountPercentage) {
  const value = Number(discountPercentage);
  if (!value || value <= 0) return null;
  const trimmed = Number.isInteger(value) ? value : value.toFixed(1);
  return `${trimmed}% off`;
}

/** Builds "N item(s)" with correct pluralization. */
export function pluralize(count, singular, plural = `${singular}s`) {
  return `${count} ${count === 1 ? singular : plural}`;
}
