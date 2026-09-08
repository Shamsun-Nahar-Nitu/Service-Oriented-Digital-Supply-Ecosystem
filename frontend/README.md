# ShopNest — Frontend

A React + Vite storefront for the ShopNest e-commerce API (Django REST
Framework, JWT auth, four user roles: Admin, Manager, Vendor, Customer).
Plain JavaScript, no TypeScript, no meta-framework — a standard client-side
SPA that talks to the API over `fetch`/axios.

## Stack

- **React 18** + **React Router 6** (client-side routing, role-gated)
- **Vite** (dev server + build)
- **Tailwind CSS** (custom design tokens — see `tailwind.config.js`)
- **axios** (API client with automatic JWT attach + refresh)
- **lucide-react** (icons)
- No Redux/Zustand — auth and cart state live in two small Context providers,
  which is all this app needs.

## Getting started

```bash
npm install
cp .env.example .env   # then edit VITE_API_BASE_URL if needed
npm run dev             # http://localhost:5173
```

```bash
npm run build            # production build to dist/
npm run preview           # serve the production build locally
npm run lint              # eslint
```

## Connecting to the backend

This frontend expects the Django API described in the project's `backend/`
repo, running with its default URL layout (`/api/v1/...`).

1. **Start the backend** (see the backend's own README for its setup —
   roughly: `pip install`, run migrations, then `python manage.py runserver`).
2. **Seed demo data** so there's something to look at:
   ```bash
   python manage.py seed_demo_data
   ```
   This creates one account per role, all with the password pattern
   `<Role>@12345`:

   | Role | Email | Password |
   |---|---|---|
   | Admin | `admin@example.com` | `Admin@12345` |
   | Manager | `manager@example.com` | `Manager@12345` |
   | Vendor | `vendor@example.com` | `Vendor@12345` |
   | Customer | `customer@example.com` | `Customer@12345` |

3. **CORS — important:** the backend's `CORS_ALLOWED_ORIGINS` defaults to
   `http://localhost:3000`, but Vite serves on **`http://localhost:5173`** by
   default. Set the backend's env var before starting it:
   ```bash
   export CORS_ALLOWED_ORIGINS=http://localhost:5173
   ```
   Skipping this step is the most common reason API calls fail with an
   opaque network/CORS error in the browser console.
4. **Point the frontend at the API** via `.env`:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

## A backend constraint that shapes this app

Every endpoint on this API requires an authenticated request — including
`GET /products/` and `GET /categories/`, which return an **empty result set**
for an anonymous user rather than a public catalog. There is no genuinely
public storefront to serve. Accordingly, the entire app (other than
`/login` and `/register`) sits behind a `<RequireAuth />` route guard — see
`src/App.jsx`. This is a real property of the backend, not a simplification
made on the frontend side.

A few other backend-driven decisions worth knowing about if you extend this:

- **The cart is 100% client-side** (`localStorage`, via `CartContext`).
  There's no cart model on the backend — checkout takes a raw
  `{shipping_address, items: [{product, quantity}]}` payload. `CartPage`
  re-validates every line item against the live product API on mount so
  stale price/stock never reaches checkout silently.
- **Products are looked up by numeric `id`, not `slug`** — the API has no
  slug-lookup route or filter, despite the model having a `slug` field.
- **Payments have no "list by transaction" filter.** `OrderDetailPage` finds
  a transaction's payment by fetching the caller's own payments and matching
  client-side — fine at this app's scale, worth revisiting if payment volume
  grows.
- **Managers can't browse the vendor list.** `/auth/users/` (needed to look
  up vendor accounts) is admin-only. `ProductForm` gives managers a plain
  numeric "Vendor ID" field instead of a picker, rather than pretending a
  lookup exists.
- **One payment per transaction, simulated.** There's no real payment
  gateway wired in — `PaymentPanel` calls the same `confirm` endpoint a real
  gateway's webhook would hit, made explicit in the UI rather than
  pretending it's a live charge.

## Project structure

```
src/
├── api/            One module per REST resource, plus the shared axios
│                   client (client.js) that attaches JWTs and refreshes
│                   them on 401.
├── context/        AuthContext, CartContext, ToastContext.
├── hooks/          useFetch (auto GET + loading/error state), useAsync
│                   (manual mutations), useDebounce, useMediaQuery.
├── components/
│   ├── ui/         Design-system primitives: Button, Input, Select, Modal,
│   │               DataTable, Pagination, Toast, StatusBadge, etc.
│   ├── layout/     Header, Footer, CategoryNav, and the per-area shells
│   │               (MainLayout, AuthLayout, VendorLayout, AdminLayout).
│   ├── product/    ProductCard, ProductGrid, ProductFilters, ProductSort.
│   ├── cart/       CartItem, CartSummary.
│   ├── orders/     OrderCard, OrderStatusTimeline, PaymentPanel.
│   ├── forms/      One form per entity (Login, Register, Profile,
│   │               ChangePassword, Product, Category, User) — each owns
│   │               its own validation/error state and calls a passed-in
│   │               onSubmit, so pages stay thin.
│   └── routing/    RequireAuth, RequireRole route guards.
├── pages/          One file per route. vendor/ and admin/ subfolders hold
│                   the role-restricted dashboards.
└── utils/          format.js (currency/date), errors.js (API error
                    envelope → readable message), constants.js (enums
                    mirrored from the backend's choice fields), palette.js
                    (deterministic product placeholder colors), cn.js.
```

## Design notes

- **No product images exist in the API.** Rather than broken `<img>` tags,
  every product renders a `ProductThumb` — a colored monogram tile derived
  deterministically from the product's SKU (`utils/palette.js`), so the same
  product always looks the same and the catalog still reads as varied.
- **Every list endpoint follows the same pagination envelope**
  (`{count, total_pages, current_page, next, previous, results}`) and every
  error follows the same shape (`{success, status_code, errors}`) — see
  `components/ui/Pagination.jsx` and `utils/errors.js`. Because both are
  handled once, centrally, individual pages never need their own
  pagination or error-parsing logic.
- **Filters live in the URL** (`ProductsPage`, `OrdersPage`,
  `AdminOrdersPage`, etc.) so a refresh, back-button press, or shared link
  reproduces the same result set instead of resetting to defaults.
