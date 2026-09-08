import { FolderTree, Package, Boxes, ClipboardList, Users } from 'lucide-react';
import { DashboardShell } from './DashboardShell';
import { useAuth } from '../../context/AuthContext';

const BASE_NAV_ITEMS = [
  { to: '/admin/products', label: 'Products', icon: Package, end: true },
  { to: '/admin/categories', label: 'Categories', icon: FolderTree },
  { to: '/admin/inventory', label: 'Inventory', icon: Boxes },
  { to: '/admin/orders', label: 'Orders', icon: ClipboardList },
];

export function AdminLayout() {
  const { isAdmin } = useAuth();
  // User account management is admin-only server-side (IsAdminRole), so the
  // nav link only appears for admins rather than 403-ing managers who click it.
  const navItems = isAdmin
    ? [...BASE_NAV_ITEMS, { to: '/admin/users', label: 'Users', icon: Users }]
    : BASE_NAV_ITEMS;

  return <DashboardShell title="Admin console" navItems={navItems} />;
}
