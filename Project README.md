# Service-Oriented Digital Supply Ecosystem

A multi-role digital commerce and supply management system with a React frontend and Django REST backend.

## Features

- Public product browsing
- Product search, filtering and sorting
- Customer shopping and cart
- Checkout and orders
- Real payment gateway integration
- Vendor product management
- Inventory management
- Role-based manager and admin panels
- JWT authentication
- BDT currency support

## Roles

| Role | Access |
|---|---|
| Customer | Shopping, checkout, payment, orders |
| Vendor | Own products and related orders |
| Manager | Products, categories, inventory, orders |
| Admin | Full system administration |

## Architecture

```text
frontend/
   │
   │ REST API + JWT
   ▼
backend/
   │
   ▼
database
```

Frontend and backend are maintained and run separately.

## Repository

```text
Service-Oriented-Digital-Supply-Ecosystem/
├── backend/
├── frontend/
└── README.md
```

See:

- [`backend/README.md`](backend/README.md)
- [`frontend/README.md`](frontend/README.md)

## Public vs Protected

Public users can browse the storefront without logging in.

Authentication is required for:

```text
Cart
Checkout
Orders
Payment
Profile changes
Vendor operations
Manager operations
Admin operations
```

Backend permissions are authoritative.

## Currency

```text
BDT / ৳
Locale: en-BD
```

## Backend Setup

```bash
cd backend

python -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt

cp .env.example .env
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Runs on:

```text
http://localhost:8000/
```

## Frontend Setup

In a separate terminal:

```bash
cd frontend

npm install
cp .env.example .env
npm run dev
```

Runs on:

```text
http://localhost:5173/
```

Frontend API configuration:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Payment

Payment is handled through the backend and configured payment gateway.

Gateway credentials stay on the backend. Payment success must be verified server-side.

## Development

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

## Development Principles

- Keep frontend and backend responsibilities separate.
- Enforce permissions in the backend.
- Do not trust client-side prices or payment status.
- Keep secrets out of source control.
- Use BDT consistently across the project.
- Keep public browsing separate from protected actions.