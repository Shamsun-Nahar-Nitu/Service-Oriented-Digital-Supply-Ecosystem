import { ROLES } from './constants';

/**
 * Single source of truth for the landing page associated with each role.
 */
export function getHomePath(role) {
  switch (role) {
    case ROLES.ADMIN:
    case ROLES.MANAGER:
      return '/admin/products';
    case ROLES.VENDOR:
      return '/vendor/products';
    case ROLES.CUSTOMER:
    default:
      return '/';
  }
}