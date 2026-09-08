/**
 * Central source of truth for enum-like values that mirror the backend's
 * choice fields (apps/users/models.py, apps/products/models.py,
 * apps/transactions/models.py, apps/payments/models.py). Keeping the labels
 * and colors here means a new status only needs to be added in one place.
 */

export const ROLES = {
  ADMIN: 'ADMIN',
  MANAGER: 'MANAGER',
  VENDOR: 'VENDOR',
  CUSTOMER: 'CUSTOMER',
};

export const ROLE_LABELS = {
  [ROLES.ADMIN]: 'Admin',
  [ROLES.MANAGER]: 'Manager',
  [ROLES.VENDOR]: 'Vendor',
  [ROLES.CUSTOMER]: 'Customer',
};

// Roles that can act as "staff" for catalog/order management purposes.
export const STAFF_ROLES = [ROLES.ADMIN, ROLES.MANAGER];

export const ORDER_STATUS = {
  PENDING: 'PENDING',
  CONFIRMED: 'CONFIRMED',
  SHIPPED: 'SHIPPED',
  DELIVERED: 'DELIVERED',
  CANCELLED: 'CANCELLED',
  REFUNDED: 'REFUNDED',
};

export const ORDER_STATUS_LABELS = {
  PENDING: 'Pending',
  CONFIRMED: 'Confirmed',
  SHIPPED: 'Shipped',
  DELIVERED: 'Delivered',
  CANCELLED: 'Cancelled',
  REFUNDED: 'Refunded',
};

// Tailwind class fragments per status, used by <StatusBadge />.
export const ORDER_STATUS_STYLES = {
  PENDING: 'bg-gold-100 text-gold-700',
  CONFIRMED: 'bg-ink-100 text-ink-700',
  SHIPPED: 'bg-ink-100 text-ink-700',
  DELIVERED: 'bg-success-100 text-success-700',
  CANCELLED: 'bg-danger-100 text-danger-700',
  REFUNDED: 'bg-danger-100 text-danger-700',
};

export const ORDER_STATUS_SEQUENCE = ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED'];

export const PRODUCT_ISSUE = {
  NONE: 'NONE',
  DAMAGED: 'DAMAGED',
  RECALLED: 'RECALLED',
  QUALITY_HOLD: 'QUALITY_HOLD',
};

export const PRODUCT_ISSUE_LABELS = {
  NONE: 'No issues',
  DAMAGED: 'Damaged',
  RECALLED: 'Recalled',
  QUALITY_HOLD: 'Quality hold',
};

export const PAYMENT_METHODS = [
  { value: 'CARD', label: 'Credit / Debit Card' },
  { value: 'UPI', label: 'UPI' },
  { value: 'NET_BANKING', label: 'Net Banking' },
  { value: 'WALLET', label: 'Wallet' },
  { value: 'COD', label: 'Cash on Delivery' },
];

export const PAYMENT_STATUS_STYLES = {
  PENDING: 'bg-gold-100 text-gold-700',
  SUCCESS: 'bg-success-100 text-success-700',
  FAILED: 'bg-danger-100 text-danger-700',
  REFUNDED: 'bg-ink-100 text-ink-700',
};

export const STOCK_MOVEMENT_LABELS = {
  RESTOCK: 'Restock',
  SALE: 'Sale',
  RETURN: 'Return',
  ADJUSTMENT: 'Adjustment',
  DAMAGE: 'Damage',
};

export const CART_STORAGE_KEY = 'shopnest.cart.v1';
export const AUTH_STORAGE_KEY = 'shopnest.auth.v1';
