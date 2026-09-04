# E-Commerce Backend

A production-style Django REST Framework backend for an e-commerce platform.
Pure JSON API — no Django templates for end users — with JWT authentication,
role-based access control, and interactive Swagger/ReDoc documentation.

## Tech stack

| Concern              | Choice                                   |
|-----------------------|-------------------------------------------|
| Framework             | Django 5 + Django REST Framework          |
| Database              | SQLite (see note below on swapping this)  |
| Auth                  | JWT via `djangorestframework-simplejwt`   |
| API docs              | `drf-spectacular` (OpenAPI 3, Swagger UI, ReDoc) |
| CORS                  | `django-cors-headers`                     |
| Filtering             | `django-filter`                           |
| Config                | `django-environ` (`.env` file)            |

## Project structure

```
ecommerce_backend/
├── .github/workflows/ci.yml    # Lint + test on every push/PR
├── .vscode/                    # Shared editor config (settings, debug configs, extensions)
├── config/                     # Project-level configuration, not business logic
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # DEBUG=True, permissive CORS
│   │   └── production.py       # Security headers, WhiteNoise static files
│   ├── urls.py                 # Root URL conf — mounts /api/v1/ and docs
│   ├── wsgi.py / asgi.py
├── apps/
│   ├── core/                   # Shared abstractions used by every app
│   │   ├── models.py           #   TimeStampedModel (created_date/updated_date)
│   │   ├── permissions.py      #   Role-based permission classes
│   │   ├── pagination.py       #   Default pagination
│   │   ├── exceptions.py       #   Consistent error response envelope
│   │   └── management/commands/seed_demo_data.py
│   ├── users/                  # Custom User model (email login, role field), JWT views
│   ├── category/               # Product categories (with subcategories)
│   ├── products/                # Product catalog, owned by vendors
│   ├── inventory/               # Stock levels + audited stock movements
│   ├── transactions/            # Orders, line items, checkout business logic
│   └── payments/                # Payments tied 1:1 to a transaction
├── requirements/
│   ├── base.txt / development.txt / production.txt
├── manage.py
├── pyproject.toml               # Ruff (lint + format) and pytest-django config
├── .env.example
```

Each app follows the same internal layout, so once you understand one you
understand all of them:

```
apps/<name>/
├── models.py        # Data + light model-level behaviour (properties, save())
├── serializers.py    # Validation + shape of request/response JSON
├── permissions.py     # App-specific permission classes (if needed beyond core)
├── views.py            # ViewSets — thin; business logic lives in services.py
├── urls.py              # Router registration for this app
├── admin.py              # Django admin registration (internal ops tool only)
└── tests/                # Test suite for this app (where present)
```

Business logic that's more than "validate and save" (checkout) lives in a
`services.py` module instead of bloating the view or serializer — see
`apps/transactions/services.py::CheckoutService`.

## Why this structure

- **`apps/core`** exists so five different apps don't each reinvent
  `created_date`/`updated_date`, role checks, and pagination slightly
  differently. Change pagination once, it changes everywhere.
- **Settings are split by environment** instead of one `settings.py` with
  `if DEBUG` branches sprinkled through it — `development.py` and
  `production.py` each only contain what's *different* from `base.py`.
- **No Django templates for the public API.** Every endpoint returns JSON.
  Templates are still wired up because the Django admin needs them
  internally, but that's an implementation detail of `/admin/`, not
  something the API consumes.
- **The custom User model uses email, not username.** This is a decision
  you cannot change after the fact once real users exist, so it's made
  correctly from migration zero.
- **Checkout is a service class, not a fat serializer or fat view.** It's
  the one piece of real business logic (validate stock → create order →
  decrement inventory → log the movement, atomically) and it's tested in
  isolation from the HTTP layer in `apps/transactions/tests/test_checkout.py`.

## Roles

The `User.role` field drives all access control. There is no separate
Django "groups" setup — role is a single field, checked by permission
classes in `apps/core/permissions.py` and per-app `permissions.py` files.

| Role       | Can do                                                                 |
|------------|-------------------------------------------------------------------------|
| `CUSTOMER` | Browse active products, check out, view/cancel their own orders, pay   |
| `VENDOR`   | Manage their own product listings; view orders containing their products (read-only) |
| `MANAGER`  | Manage categories/products/inventory for everyone; update order status |
| `ADMIN`    | Everything a Manager can do, plus manage user accounts and roles       |

Self-registration (`POST /api/v1/auth/register/`) only allows `CUSTOMER` or
`VENDOR`. Admin and Manager accounts must be created by an existing admin
via `POST /api/v1/auth/users/` — this is deliberate, so privilege escalation
isn't a single unauthenticated API call away.

## Getting started

```bash
cd ecommerce_backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements/development.txt

cp .env.example .env              # then edit SECRET_KEY etc.

python manage.py migrate
python manage.py seed_demo_data   # optional: creates one user per role + sample products
python manage.py runserver
```

The API is now at `http://localhost:8000/api/v1/`.

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Raw OpenAPI schema: `http://localhost:8000/api/schema/`
- Django admin (internal ops only): `http://localhost:8000/admin/`

If you ran `seed_demo_data`, you can log in immediately as:

| Role     | Email                  | Password        |
|----------|------------------------|-----------------|
| Admin    | admin@example.com      | Admin@12345     |
| Manager  | manager@example.com    | Manager@12345   |
| Vendor   | vendor@example.com     | Vendor@12345    |
| Customer | customer@example.com   | Customer@12345  |

## Running tests

```bash
python manage.py test
# or, equivalently (pytest-django is configured via pyproject.toml):
pytest
```

## Linting & formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and
formatting — one tool, one config (`pyproject.toml`), no Black/isort/flake8
juggling.

```bash
ruff check .            # lint
ruff format .           # format
ruff check . --fix      # auto-fix what's safely fixable
```

If you're using VS Code with the recommended extensions (see below), this
runs automatically on save.

## Working in VS Code

The repo ships with a `.vscode/` folder (committed on purpose — this is
shared project config, not personal preference) that gives you:

- **`settings.json`** — points VS Code at `venv/bin/python`, enables
  format-on-save with Ruff, and wires up `pytest` as the test runner so
  Django's test suite shows up in the Testing sidebar.
- **`launch.json`** — three ready-to-use debug configs: *Django: Run
  Server*, *Django: Test Suite*, and *Django: Seed Demo Data*. Set a
  breakpoint anywhere in the code and hit F5.
- **`extensions.json`** — VS Code will prompt you to install the handful of
  extensions this config depends on (Python, Pylance, Ruff, Django syntax,
  GitLens) the first time you open the folder.

First time opening the project:

1. Create the venv and install dependencies (see *Getting started* above)
   so `venv/bin/python` actually exists for VS Code to find.
2. Open the folder in VS Code, accept the extension recommendations prompt.
3. `Cmd/Ctrl+Shift+P` → **Python: Select Interpreter** → pick
   `./venv/bin/python` if VS Code hasn't already picked it up.
4. Open the Testing sidebar — you should see all tests discovered under
   `apps/*/tests/`.

## Continuous Integration

`.github/workflows/ci.yml` runs on every push and pull request to `main`:
Ruff lint, a check for missing migrations, and the full test suite, on
Python 3.12. No secrets or external services are needed — it runs entirely
against SQLite. This is the safety net that catches "works on my machine"
before it reaches `main`.

## Authentication flow

```bash
# 1. Register (customer or vendor only)
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","first_name":"Jane","role":"CUSTOMER","password":"StrongPass123","confirm_password":"StrongPass123"}'

# 2. Log in to get a JWT pair
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"StrongPass123"}'
# -> {"access": "...", "refresh": "...", "user": {...}}

# 3. Use the access token on subsequent requests
curl http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer <access_token>"

# 4. Refresh when the access token expires
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## Endpoint overview

All routes are prefixed with `/api/v1/`.

| Area          | Endpoint                                    | Notes                                   |
|---------------|----------------------------------------------|-------------------------------------------|
| Auth          | `POST /auth/register/`                        | Public. Customer/Vendor only.             |
| Auth          | `POST /auth/login/`                           | Returns JWT pair + user info.             |
| Auth          | `POST /auth/token/refresh/`                   | Exchange refresh token for new access.    |
| Auth          | `GET/PATCH /auth/me/`                          | Own profile.                              |
| Auth          | `POST /auth/change-password/`                  | Own password.                             |
| Auth          | `/auth/users/` (full CRUD)                     | Admin only — manage any account/role.     |
| Categories    | `/categories/` (full CRUD)                     | Read: anyone authenticated. Write: admin/manager. |
| Products      | `/products/` (full CRUD)                       | Read: role-scoped visibility. Write: admin/manager/owning vendor. Filters: `category`, `vendor`, `brand`, `issues`, `min_price`, `max_price`, `in_stock`. |
| Inventory     | `/inventory/` (full CRUD)                      | Admin/manager only.                       |
| Inventory     | `POST /inventory/{id}/restock/`                | Adds stock, logs a StockMovement.         |
| Inventory     | `GET /inventory/{id}/movements/`               | Audit trail for one product's stock.      |
| Transactions  | `POST /transactions/checkout/`                 | Cart → order. Validates stock atomically. |
| Transactions  | `GET /transactions/`, `/transactions/{id}/`     | Role-scoped: own orders / own-product orders / everything. |
| Transactions  | `PATCH /transactions/{id}/update_status/`       | Admin/manager order lifecycle control.    |
| Transactions  | `POST /transactions/{id}/cancel/`               | Customer can cancel their own pending order. |
| Payments      | `POST /payments/`                               | Initiate payment for an owned transaction.|
| Payments      | `POST /payments/{id}/confirm/`                  | Simulates a gateway success/failure callback — this is where a real Stripe/Razorpay webhook handler would plug in. |

Every response uses a consistent shape. Success responses are the plain
serialized resource (or a paginated envelope with `count`/`results`/etc. for
list views); errors always look like:

```json
{
  "success": false,
  "status_code": 400,
  "errors": { "field_name": ["What went wrong."] }
}
```

## Swapping SQLite for Postgres later

SQLite is fine for development and is what this project ships with, but for
production traffic you'll likely want Postgres. Because the project only
touches the database through Django's ORM, the change is contained to
`config/settings/production.py`:

```python
DATABASES = {
    "default": env.db("DATABASE_URL")  # requires psycopg2-binary + dj-database-url
}
```

No app code needs to change.

## Extending this project

- **Add a new domain concept** (e.g. Reviews): create `apps/reviews/` following
  the same file layout as the existing apps, add it to `LOCAL_APPS` in
  `config/settings/base.py`, and wire its `urls.py` into `config/urls.py`.
- **Add a new role or permission rule**: extend `User.Role` in
  `apps/users/models.py` and add/adjust a permission class in
  `apps/core/permissions.py` — everything importing from there picks it up.
- **Add a real payment gateway**: replace the body of
  `PaymentViewSet.confirm` (or add a webhook endpoint) that calls
  `Payment.mark_successful()` / `Payment.mark_failed()` based on the
  gateway's actual callback payload — the state machine is already in
  `apps/payments/models.py`.
