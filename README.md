# Multi-Vendor E-Commerce

[![CI](https://github.com/17pavankumar/multi-vendor/actions/workflows/ci.yml/badge.svg)](https://github.com/17pavankumar/multi-vendor/actions/workflows/ci.yml)

A multi-vendor marketplace — customers, vendors, and admins each get
their own flows — built with:

```
React  →  Django REST Framework  →  MySQL
                  ↓
                Redis  →  Celery (async tasks, scheduled jobs)
                  ↓
                Docker
```

Payments are handled via **Razorpay**.

## Status

This project is being built incrementally, one reviewable phase at a
time. Backend is feature-complete; frontend is in progress.

- [x] Repo scaffold, Docker Compose (MySQL, Redis, Django, Celery worker/beat, React), `db/schema.sql`
- [x] Auth: custom email/role-based user model, JWT login (with role embedded in the token), registration, profile, addresses
- [x] CI: lint (ruff) + real test suite + migrations, all run against an actual MySQL service container
- [x] Vendor approval, categories & products, inventory
- [x] Cart, wishlist, coupons
- [x] Checkout, orders, Razorpay payments
- [x] Shipping / live tracking
- [x] Reviews
- [x] Admin: commission rules, vendor payouts (Celery), platform reports
- [ ] React frontend — auth (register/login/logout) done; browse/cart/checkout/vendor/admin dashboards in progress

## Project layout

```
backend/
  config/          Django project settings, root urls, Celery app
  apps/            one Django app per feature domain (users, vendors, products, orders, ...)
    <app>/
      models/      one file per model
      serializers/ one file per feature
      views/       one file per feature
      tests/       one file per feature
db/
  schema.sql       hand-written MySQL schema — the source of truth for the data model
frontend/
  src/
    api/           thin fetch wrapper (client.js) + one file per domain's API calls
    context/       AuthContext — JWT storage, decoded user/role, login/register/logout
    components/    shared UI (Layout/navbar, ProtectedRoute)
    features/      one folder per feature (auth, cart, checkout, vendor-dashboard, ...)
    pages/         top-level pages not tied to one feature (Home, 404)
```

## Running locally

```bash
cp .env.example .env   # fill in real values
docker compose up --build
```

- API: http://localhost:8000
- Frontend: http://localhost:5173

## Running backend tests

```bash
docker compose exec backend pytest
docker compose exec backend ruff check .
```

## Running frontend checks

```bash
cd frontend
npm install
npm run lint
npm run build
```
