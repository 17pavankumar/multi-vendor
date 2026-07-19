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
time. Done so far:

- [x] Repo scaffold, Docker Compose (MySQL, Redis, Django, Celery worker/beat, React), `db/schema.sql`
- [x] Auth: custom email/role-based user model, JWT login (with role embedded in the token), registration, profile, addresses
- [x] CI: lint (ruff) + real test suite + migrations, all run against an actual MySQL service container
- [ ] Vendor approval, categories & products, inventory
- [ ] Cart, wishlist, coupons
- [ ] Checkout, orders, Razorpay payments
- [ ] Shipping / live tracking
- [ ] Reviews
- [ ] Admin: commission, reports
- [ ] React frontend

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
  src/features/    one folder per feature (auth, cart, checkout, vendor-dashboard, ...)
```

## Running locally

```bash
cp .env.example .env   # fill in real values
docker compose up --build
```

- API: http://localhost:8000
- Frontend: http://localhost:5173 (once Phase 7 lands)

## Running backend tests

```bash
docker compose exec backend pytest
docker compose exec backend ruff check .
```
