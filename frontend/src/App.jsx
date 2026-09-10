import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { ToastProvider } from './context/ToastContext';
import { ToastViewport } from './components/ui/Toast';

import { RequireAuth } from './components/routing/RequireAuth';
import { RequireRole } from './components/routing/RequireRole';

import { MainLayout } from './components/layout/MainLayout';
import { AuthLayout } from './components/layout/AuthLayout';
import { VendorLayout } from './components/layout/VendorLayout';
import { AdminLayout } from './components/layout/AdminLayout';

import HomePage from './pages/HomePage';
import ProductsPage from './pages/ProductsPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import OrdersPage from './pages/OrdersPage';
import OrderDetailPage from './pages/OrderDetailPage';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';
import UnauthorizedPage from './pages/UnauthorizedPage';
import PaymentSuccessPage from './pages/PaymentSuccessPage';
import PaymentFailPage from './pages/PaymentFailPage';
import PaymentCancelPage from './pages/PaymentCancelPage';

import VendorProductsPage from './pages/vendor/VendorProductsPage';
import VendorProductFormPage from './pages/vendor/VendorProductFormPage';
import VendorOrdersPage from './pages/vendor/VendorOrdersPage';

import AdminProductsPage from './pages/admin/AdminProductsPage';
import AdminProductFormPage from './pages/admin/AdminProductFormPage';
import AdminCategoriesPage from './pages/admin/AdminCategoriesPage';
import AdminInventoryPage from './pages/admin/AdminInventoryPage';
import AdminOrdersPage from './pages/admin/AdminOrdersPage';
import AdminUsersPage from './pages/admin/AdminUsersPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <ToastProvider>
            <Routes>
              <Route element={<AuthLayout />}>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
              </Route>

              <Route element={<MainLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/products" element={<ProductsPage />} />
                <Route path="/products/:id" element={<ProductDetailPage />} />
              </Route>

              <Route path="/payment/success" element={<PaymentSuccessPage />} />
              <Route path="/payment/fail" element={<PaymentFailPage />} />
              <Route path="/payment/cancel" element={<PaymentCancelPage />} />

              <Route element={<RequireAuth />}>
                <Route element={<RequireRole roles={['CUSTOMER']} />}>
                  <Route element={<MainLayout />}>
                    <Route path="/cart" element={<CartPage />} />
                    <Route path="/checkout" element={<CheckoutPage />} />
                    <Route path="/orders" element={<OrdersPage />} />
                    <Route path="/orders/:id" element={<OrderDetailPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                  </Route>
                </Route>

                <Route element={<RequireRole roles={['VENDOR']} />}>
                  <Route element={<VendorLayout />}>
                    <Route path="/vendor/products" element={<VendorProductsPage />} />
                    <Route path="/vendor/products/new" element={<VendorProductFormPage />} />
                    <Route path="/vendor/products/:id/edit" element={<VendorProductFormPage />} />
                    <Route path="/vendor/orders" element={<VendorOrdersPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                  </Route>
                </Route>

                <Route element={<RequireRole roles={['ADMIN', 'MANAGER']} />}>
                  <Route element={<AdminLayout />}>
                    <Route path="/admin/products" element={<AdminProductsPage />} />
                    <Route path="/admin/products/new" element={<AdminProductFormPage />} />
                    <Route path="/admin/products/:id/edit" element={<AdminProductFormPage />} />
                    <Route path="/admin/categories" element={<AdminCategoriesPage />} />
                    <Route path="/admin/inventory" element={<AdminInventoryPage />} />
                    <Route path="/admin/orders" element={<AdminOrdersPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                  </Route>
                </Route>

                <Route element={<RequireRole roles={['ADMIN']} />}>
                  <Route element={<AdminLayout />}>
                    <Route path="/admin/users" element={<AdminUsersPage />} />
                  </Route>
                </Route>
              </Route>

              <Route path="/unauthorized" element={<UnauthorizedPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
            <ToastViewport />
          </ToastProvider>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
