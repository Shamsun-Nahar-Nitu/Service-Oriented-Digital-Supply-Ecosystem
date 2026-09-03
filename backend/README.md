# E-Commerce Backend

A production-structured Django REST API for an e-commerce platform: users,
categories, products, inventory, transactions (orders) and payments, with
JWT authentication, role-based access control, CORS, and interactive API
docs via Swagger UI.

This is an API-only backend. There are no server-rendered pages/templates -
it's meant to be consumed by a separate frontend (web, mobile, etc).

---

## 1. Tech stack

| Concern            | Choice                                   |
|---------------------|-------------------------------------------|
| Framework           | Django 5.2 (LTS) + Django REST Framework  |
| Auth                | JWT via `djangorestframework-simplejwt`   |
| API docs            | `drf-spectacular` (OpenAPI 3 + Swagger UI)|
| CORS                | `django-cors-headers`                     |
| Filtering           | `django-filter`                           |
| Database            | SQLite3 (swappable via `.env`)            |
| Config              | `django-environ` (12-factor `.env` file)  |

---

## 2. Project structure

```
ecommerce_backend/
├── manage.py
├── requirements.txt
├── .env.example              # copy to .env
├── project/                  # Django project wiring only, no business logic
│   ├── settings.py
│   ├── urls.py                # /admin/, /api/schema/, /api/redoc/, /doc/
│   ├── api_urls.py            # aggregates every app's routes under /api/
│   ├── wsgi.py / asgi.py
├── apps/
│   ├── common/                # shared base models, permissions, pagination
│   ├── users/                 # custom User model (roles), JWT auth endpoints
│   ├── categories/            # product categories (self-referencing tree)
│   ├── products/              # catalog
│   ├── inventory/             # stock levels per product
│   ├── transactions/          # orders (Transaction + TransactionItem)
│   └── payments/              # payment records per order
└── logs/                      # rotating app.log (gitignored)
```

Each app follows the same internal layout: `models.py`, `serializers.py`,
`views.py`, `urls.py`, `admin.py`, `apps.py` (+ `permissions.py`/`filters.py`
where relevant). If you need to change how products work, everything you
need is in `apps/products/`- nothing product-related leaks into other apps.

---

## 3. Roles & access control

Defined once in `apps/users/models.py::User.Role` and enforced through
shared permission classes in `apps/common/permissions.py`:

| Role      | Can do |
|-----------|--------|
| **admin**    | Everything. Manage users, categories, products, inventory, all orders/payments. |
| **manager**  | Same operational access as admin (catalog, inventory, orders, payments) but cannot manage user accounts. |
| **vendor**   | Create/edit/delete their **own** products and inventory. Read-only on everything else. |
| **customer** | Browse categories/products (read-only), place orders, pay for their **own** orders. |

Public self-registration (`POST /api/auth/register/`) only allows the
`customer` and `vendor` roles. Admin/manager accounts must be created by an
existing admin (via `POST /api/auth/users/` or Django admin).

---

## 4. Data model overview

- **User** - custom, email-based login, unique `id`, `role` field, timestamps.
- **Category** - self-referencing `parent` for subcategories.
- **Product** - `sku`, `product_name`, `brand`, `issues` (known defects/recalls),
  `expire_date`, `mrp`, `discount_percent`. `selling_price` is a computed
  property (never stored/duplicated) so it can't go stale.
- **Inventory** - one-to-one with Product. `quantity_available`,
  `reorder_level`, restock/deduct helper methods.
- **Transaction** - an order. Holds a `user`, `status`, and a computed
  `total_amount`. Line items live in **TransactionItem** (product, quantity,
  `unit_price` frozen at purchase time).
- **Payment** - one-to-one with Transaction. `method` (COD/card/UPI/net
  banking/wallet/bank transfer), `status`, `amount` (always derived from the
  transaction total server-side, never trusted from the client).

Placing an order (`POST /api/transactions/`) atomically creates the
transaction, its line items, and deducts stock from inventory in a single
DB transaction - if stock is insufficient, nothing is created.

---

## 5. Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env: set a real DJANGO_SECRET_KEY, and CORS_ALLOWED_ORIGINS for your frontend.

# 4. Run migrations (creates db.sqlite3)
python manage.py migrate

# 5. Create an admin account
python manage.py createsuperuser

# 6. Run the dev server
python manage.py runserver
```

Now visit:

- **Swagger UI**: http://127.0.0.1:8000/doc/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **Raw OpenAPI schema**: http://127.0.0.1:8000/api/schema/
- **Django admin**: http://127.0.0.1:8000/admin/

---

## 6. Authentication flow

1. `POST /api/auth/register/` - sign up (customer/vendor only).
2. `POST /api/auth/login/` - exchange email+password for `access` + `refresh` JWTs.
3. Send `Authorization: Bearer <access_token>` on every subsequent request.
4. `POST /api/auth/refresh/` - get a new access token from the refresh token.
5. `POST /api/auth/logout/` - blacklist a refresh token (server-side logout).

**Using Swagger UI with JWT:** click the "Authorize" button, paste
`Bearer <access_token>` (include the word "Bearer"), and every request the
docs UI sends will be authenticated.

---

## 7. Key endpoints

| Method & path | Who | Purpose |
|---|---|---|
| `POST /api/auth/register/` | anyone | sign up as customer/vendor |
| `POST /api/auth/login/` | anyone | get JWT pair |
| `GET/PATCH /api/auth/me/` | authenticated | view/edit own profile |
| `POST /api/auth/change-password/` | authenticated | change own password |
| `GET/POST /api/auth/users/` | admin | manage all accounts |
| `GET/POST /api/categories/` | read: all, write: admin/manager | catalog categories |
| `GET/POST /api/products/` | read: all, write: admin/manager/vendor(own) | catalog |
| `GET/POST /api/inventory/` | admin/manager/vendor(own) | stock levels |
| `POST /api/inventory/{id}/restock/` | admin/manager | add stock |
| `GET/POST /api/transactions/` | own orders (staff see all) | place/list orders |
| `POST /api/transactions/{id}/cancel/` | owner/staff | cancel + restock |
| `GET/POST /api/payments/` | own payments (staff see all) | pay for an order |
| `POST /api/payments/{id}/mark_success/` | admin/manager | confirm payment |

Full request/response schemas for every field are in Swagger UI - this
table is just a map to get you oriented.

---

## 8. Design decisions worth knowing about

- **No Django templates for the app itself.** `django.contrib.admin` still
  needs the template engine internally, so `TEMPLATES` is configured, but no
  app in this project renders HTML - it's a pure JSON API.
- **Role is a plain enum, not Django Groups/Permissions.** With exactly four
  fixed roles, an enum + explicit permission classes is far easier to audit
  than dynamically assignable permissions would be.
- **Prices are never trusted from the client.** `Product.selling_price` is
  computed from `mrp`/`discount_percent`; `TransactionItem.unit_price` is
  captured server-side at order time; `Payment.amount` is always derived
  from `Transaction.total_amount`.
- **Uniform error shape.** Every API error returns
  `{"success": false, "errors": {...}}` via a shared DRF exception handler
  (`apps/common/exceptions.py`), so a frontend never has to special-case
  different error formats.
- **Soft-deactivation over hard deletes** for `User` and cancellation-based
  stock restoration for `Transaction`, so historical orders/payments always
  keep valid references.

---
