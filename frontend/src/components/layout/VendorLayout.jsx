import { Package, PlusCircle, ClipboardList, LayoutDashboard } from 'lucide-react';
import { DashboardShell } from './DashboardShell';

const NAV_ITEMS = [
  { to: '/vendor/dashboard', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/vendor/products', label: 'My products', icon: Package },
  { to: '/vendor/products/new', label: 'Add product', icon: PlusCircle },
  { to: '/vendor/orders', label: 'Orders', icon: ClipboardList },
];

export function VendorLayout() {
  return <DashboardShell title="Vendor" navItems={NAV_ITEMS} />;
}