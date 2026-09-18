import { FolderTree, Package, Boxes, ClipboardList, Users, LayoutDashboard, Activity } from 'lucide-react';
import { DashboardShell } from './DashboardShell';
import { useAuth } from '../../context/AuthContext';

// Managers land on Monitoring (vendor/customer oversight) by default —
// admins get an extra Dashboard entry ahead of it for platform revenue,
// which only IsAdmin can actually load server-side (see apps.finance.views).
const MANAGER_ITEMS = [
  { to: '/admin/monitoring', label: 'Monitoring', icon: Activity, end: true },
  { to: '/admin/products', label: 'Products', icon: Package },
  { to: '/admin/categories', label: 'Categories', icon: FolderTree },
  { to: '/admin/inventory', label: 'Inventory', icon: Boxes },
  { to: '/admin/orders', label: 'Orders', icon: ClipboardList },
];

const ADMIN_ITEMS = [
  { to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard, end: true },
  ...MANAGER_ITEMS.map((item) => ({ ...item, end: false })),
  { to: '/admin/users', label: 'Users', icon: Users },
];

export function AdminLayout() {
  const { isAdmin } = useAuth();
  return <DashboardShell title="Admin console" navItems={isAdmin ? ADMIN_ITEMS : MANAGER_ITEMS} />;
}