# Service-Oriented Digital Supply Ecosystem — Frontend

React frontend for the Service-Oriented Digital Supply Ecosystem.

Provides the public storefront and separate interfaces for customers, vendors, managers and admins.

## Stack

* React 18
* Vite
* React Router 6
* Tailwind CSS
* Axios
* React Context API
* lucide-react

## Structure

```text
frontend/
├── public/
├── src/
│   ├── api/
│   ├── components/
│   ├── context/
│   ├── hooks/
│   ├── pages/
│   └── utils/
├── package.json
└── vite.config.js
```

## Panels

* **Customer** — shopping, cart, checkout, payment and orders
* **Vendor** — own product management and related orders
* **Manager** — products, categories, inventory and operational orders
* **Admin** — full administration

Role-specific routes are protected by frontend guards and backend permissions.

## Public Storefront

No login is required for:

* Home
* Products
* Product details
* Categories
* Search
* Filtering
* Sorting

Login is required for protected actions such as cart changes, checkout, orders, payment, profile updates and management operations.

## Authentication

JWT authentication is provided by the backend.

Main authentication state:

```text
src/context/AuthContext.jsx
```

Token/API handling:

```text
src/api/
```

## API

Configure the backend URL in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Currency

```env
VITE_CURRENCY_CODE=BDT
VITE_CURRENCY_LOCALE=en-BD
```

Display currency:

```text
৳ / BDT
```

Use the shared formatter for prices.

## Payment

Payment is initiated through the backend and verified server-side.

The frontend must not:

* store gateway secrets
* validate payment authenticity
* mark payments as successful independently

## Setup

```bash
cd frontend

npm install
cp .env.example .env
npm run dev
```

Development server:

```text
http://localhost:5173/
```

## Scripts

```bash
npm run dev
npm run build
npm run preview
npm run lint
```

## Notes

* Keep API calls inside `src/api/`.
* Keep shared auth state in `AuthContext`.
* Keep cart state in `CartContext`.
* Use route guards for protected pages.
* Backend remains the source of truth for business data.
* Never expose backend or payment secrets through frontend environment variables.
