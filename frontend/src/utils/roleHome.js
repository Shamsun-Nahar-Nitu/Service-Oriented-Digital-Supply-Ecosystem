import { ROLES } from './constants';

/**
 * Single source of truth for the landing page associated with each role.
 */
export function getHomePath(role) {
  switch (role) {
    case ROLES.ADMIN:
      return '/admin/dashboard';
    case ROLES.MANAGER:
      return '/admin/monitoring';
    case ROLES.VENDOR:
      return '/vendor/dashboard';
    case ROLES.CUSTOMER:
    default:
      return '/';
  }
}