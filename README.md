# MiniStore Checkout Platform

A secure checkout backend demonstrating how to build a Stripe-powered payment flow with verified webhooks, reliable order state transitions, and PostgreSQL-based audit trails suitable for real-world deployments.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
  - [1.1 What problem this system solves](#11-what-problem-this-system-solves)
  - [1.2 Business value](#12-business-value)
  - [1.3 High-level system purpose](#13-high-level-system-purpose)
  - [1.4 Target users / stakeholders](#14-target-users--stakeholders)

- [2. System Architecture (High Level)](#2-system-architecture-high-level)
  - [2.1 High-level architecture description](#21-high-level-architecture-description)
  - [2.2 Major components](#22-major-components)
  - [2.3 Request/response flow overview](#23-requestresponse-flow-overview)
  - [2.4 Deployment topology (high level)](#24-deployment-topology-high-level)

- [3. Technology Stack](#3-technology-stack)
  - [3.1 Backend framework & language](#31-backend-framework--language)
  - [3.2 Database](#32-database)
  - [3.3 Third-party services](#33-third-party-services)
  - [3.4 Infrastructure components](#34-infrastructure-components)
  - [3.5 Tooling](#35-tooling)

- [4. Key Features & Capabilities](#4-key-features--capabilities)
  - [4.1 Core business features](#41-core-business-features)
  - [4.2 Admin features](#42-admin-features)
  - [4.3 Security features](#43-security-features)
  - [4.4 Integration points](#44-integration-points)

- [5. Repository Structure](#5-repository-structure)
  - [Where Things Live](#where-things-live)

- [6. Environment Setup (Local Development)](#6-environment-setup-local-development)
  - [6.1 Prerequisites](#61-prerequisites)
  - [6.2 Python & virtual environment](#62-python--virtual-environment)
  - [6.3 Install dependencies](#63-install-dependencies)
  - [6.4 Environment variable setup](#64-environment-variable-setup)
  - [6.5 Local PostgreSQL setup](#65-local-postgresql-setup)
  - [6.6 Running migrations](#66-running-migrations)
  - [6.7 Create a superuser (for admin access)](#67-create-a-superuser-for-admin-access)
  - [6.8 Run the server](#68-run-the-server)

- [7. Configuration & Secrets Management](#7-configuration--secrets-management)
  - [7.1 Environment variables](#71-environment-variables)
  - [7.2 Secrets handling](#72-secrets-handling)
  - [7.3 Different environments (dev / staging / prod)](#73-different-environments-dev--staging--prod)
  - [7.4 Configuration best practices](#74-configuration-best-practices)

- [8. Database & Migrations](#8-database--migrations)
  - [8.1 PostgreSQL usage](#81-postgresql-usage)
  - [8.2 Migration strategy](#82-migration-strategy)
  - [8.3 Schema management](#83-schema-management)
  - [8.4 Data integrity considerations](#84-data-integrity-considerations)
  - [8.5 Backup / restore (high level)](#85-backup--restore-high-level)

- [9. API Documentation](#9-api-documentation)
  - [9.1 Base URL (example)](#91-base-url-example)
  - [9.2 Authentication method](#92-authentication-method)
  - [9.3 API versioning](#93-api-versioning)
  - [9.4 Example endpoint: POST /api/checkout/](#94-example-endpoint-post-apicheckout)
  - [Error handling conventions](#error-handling-conventions)

- [10. Security Considerations](#10-security-considerations)
  - [10.1 Authentication & authorization](#101-authentication--authorization)
  - [10.2 CSRF / CORS](#102-csrf--cors)
  - [10.3 Data protection](#103-data-protection)
  - [10.4 Secrets & key handling](#104-secrets--key-handling)
  - [10.5 Audit / logging considerations](#105-audit--logging-considerations)

- [11. Logging & Monitoring](#11-logging--monitoring)
  - [11.1 Logging approach](#111-logging-approach)
  - [11.2 Log levels](#112-log-levels)
  - [11.3 Error tracking](#113-error-tracking)
  - [11.4 Operational visibility](#114-operational-visibility)

- [12. Testing Strategy](#12-testing-strategy)
  - [12.1 Unit tests](#121-unit-tests)
  - [12.2 Integration tests](#122-integration-tests)
  - [12.3 How to run tests](#123-how-to-run-tests)
  - [12.4 Test coverage expectations](#124-test-coverage-expectations)

- [13. Deployment Guide (High Level)](#13-deployment-guide-high-level)
  - [13.1 Supported environments](#131-supported-environments)
  - [13.2 Deployment flow (example)](#132-deployment-flow-example)
  - [13.3 Required services](#133-required-services)
  - [13.4 Pre-deployment checklist](#134-pre-deployment-checklist)
  - [13.5 Post-deployment validation](#135-post-deployment-validation)

- [14. Rollback & Recovery](#14-rollback--recovery)
  - [14.1 Rollback strategy](#141-rollback-strategy)
  - [14.2 DB rollback considerations](#142-db-rollback-considerations)
  - [14.3 Disaster recovery overview](#143-disaster-recovery-overview)

- [15. Contribution Guidelines (for Team)](#15-contribution-guidelines-for-team)
  - [15.1 Coding standards](#151-coding-standards)
  - [15.2 Branching strategy](#152-branching-strategy)
  - [15.3 Pull Request (PR) process](#153-pull-request-pr-process)
  - [15.4 Code review expectations](#154-code-review-expectations)

## 1. Project Overview

MiniStore Checkout transcends being a simple technical demonstration to establish itself as a production-grade reference architecture for integrating modern payment processing into Django-based applications. The project meticulously embodies enterprise-level architectural patterns while maintaining deliberate, thoughtful minimalism, strategically balancing sophistication with accessibility. It serves a dual purpose: as an educational masterclass for developers seeking to understand payment integration complexities, and as a production-ready foundation that organizations can confidently deploy, extend, and scale for real-world e-commerce operations.

### 1.1 What problem this system solves

MiniStore Checkout Platform provides a **small but real-world** example of:

- Creating **orders and line items** in an internal system.
- Redirecting the user to **Stripe Checkout** for secure payment.
- Using **Stripe webhooks** to mark the internal order as **PAID** in a safe, idempotent way.
- Showing users a simple **“My Paid Orders”** view driven by webhook-confirmed data.

In other words, it demonstrates **how to correctly integrate a payment provider into a Django backend** without mixing payment logic directly into the web UI or storing insecure card data.

### 1.2 Business value

From a business point of view, this system:

- Provides a **reference implementation** for any team that wants to add **Stripe-based checkout** to their product.
- Reduces time-to-market by demonstrating:
  - How to structure the **order lifecycle** (CREATED → PAID → FAILED).
  - How to **avoid double-charging** through webhook idempotency.
  - How to keep your own database as the **source of truth** instead of trusting the frontend URL alone.
- Serves as a **technical asset** for:
  - Sales/pre-sales teams that need a live demo for clients.
  - Engineering teams that need a canonical pattern to replicate across services.

### 1.3 High-level system purpose

At a high level, this system:

- Provides a **simple catalog** of products (in code) that users can “buy”.
- Creates **Order** and **OrderItem** rows in PostgreSQL when a checkout is started.
- Creates a **Stripe Checkout Session** and returns its URL.
- Waits for **Stripe to notify us via webhook** when the user has paid.
- Updates the order to **PAID** and displays it to the user.

The important part is not the UI or the catalog; it is the **correct handling of payment flows**, **webhooks**, and **idempotent updates** to internal state.

### 1.4 Target users / stakeholders

- **Backend Developers** – extend business logic, add new payment methods, refactor services.
- **DevOps / Platform Engineers** – deploy the service, wire environment variables, monitor DB and webhooks.
- **QA Engineers** – validate critical flows (checkout success, cancellation, webhook retries, error cases).
- **Technical Product Owners / Architects** – review architecture, data model, and integration patterns with Stripe.
- **Future maintainers** – use this as a clean base to evolve into a larger checkout service.

---

## 2. System Architecture (High Level)

### 2.1 High-level architecture description

The system is a **single Django project** with:

- A **UI layer** (Django views + templates + minimal JS).
- An **API layer** (Django REST Framework view for `/api/checkout/`).
- A **service layer** (Python modules handling checkout, Stripe, and order persistence).
- A **webhook endpoint** for Stripe events.
- A **PostgreSQL database** holding orders and Stripe event metadata.

Stripe acts as an external payment processor. The system does **not** store any card data; it only stores opaque Stripe identifiers (checkout session ID, payment intent ID) and status.

### 2.2 Major components

- **Backend (Django + DRF)**
  - Project: `config/`
  - Application: `store/`
  - API endpoints under `/api/` for programmatic access.
  - UI endpoints under `/`.

- **Database (PostgreSQL)**
  - Database name (example): `ministore_checkout`
  - Tables:
    - `store_order` – one row per order.
    - `store_orderitem` – one row per line item.
    - `store_stripeevent` – one row per webhook event (for idempotency + debugging).

- **External services**
  - **Stripe API** (REST) – used to create Checkout Sessions and track payments.
  - **Stripe Webhooks** – POST callbacks to `/stripe/webhook/`.
  - **Stripe CLI** – optional, used locally to forward webhooks and to simulate events.

### 2.3 Request/response flow overview

Typical **happy path**:

1. User logs in (`/accounts/login/`) and visits `/`.
2. UI shows available products and a “Checkout” button; JS posts to `/api/checkout/` with selected quantities.
3. `/api/checkout/`:
   - Validates payload.
   - Creates an `Order` + associated `OrderItem` rows.
   - Creates a Stripe Checkout Session.
   - Stores `stripe_checkout_session_id` on the order.
   - Returns a JSON response with `checkout_url`.
4. Frontend JS redirects user to Stripe Checkout.
5. User pays on Stripe’s hosted page.
6. Stripe calls `/stripe/webhook/` with `checkout.session.completed` event.
7. Webhook handler:
   - Validates Stripe signature.
   - Ensures `StripeEvent` row is created once (idempotent).
   - Finds the matching `Order`.
   - Calls `order.mark_paid(payment_intent_id=...)`.
8. When the user is redirected back with `?checkout=success`, the home page shows a list of **paid orders**.

### 2.4 Deployment topology (high level)

For local and small deployments:

- **Single Django application instance** running under:
  - `runserver` (development), or
  - `gunicorn`/`uvicorn` behind a reverse proxy (production).
- **Single PostgreSQL instance** running locally or as a managed service.
- **Stripe** runs externally; webhooks must be accessible over HTTPS in production.
- **Stripe CLI** is used locally to tunnel webhooks to `127.0.0.1:8000/stripe/webhook/`.

In a production environment, you would typically have:

- 1+ application instances behind a load balancer.
- Managed PostgreSQL (RDS, Cloud SQL, etc.).
- HTTPS termination at the load balancer / ingress.
- Monitoring and logging for both app and DB.

---

## 3. Technology Stack

### 3.1 Backend framework & language

- **Language**: Python (tested with 3.11+ / 3.13 in development)
- **Framework**: Django 6.x
- **API Layer**: Django REST Framework
- **Task Model**: Synchronous (no Celery/RQ in this minimal version)

### 3.2 Database

- **PostgreSQL**
  - Used as the primary relational database.
  - All application state (orders, items, Stripe event ids) is persisted here.
  - Assumes a standard `public` schema.

### 3.3 Third-party services

- **Stripe**
  - Used for:
    - Checkout Session creation.
    - Payment processing.
    - Webhooks for `checkout.session.completed` (and possibly other events later).
  - Keys and webhook secrets are provided via environment variables.

### 3.4 Infrastructure components

- **Local development**: `python manage.py runserver`
- **Webhooks (development)**: Stripe CLI `stripe listen --forward-to http://127.0.0.1:8000/stripe/webhook/`
- **Static files**: served by Django in dev, by web server or CDN in production.

### 3.5 Tooling

- **pytest + pytest-django** for tests.
- **django-environ** (or similar) for environment variable-based configuration.
- **pgAdmin / psql** for PostgreSQL inspection (optional).
- **Stripe CLI** for local webhook forwarding and test event triggering.

---

## 4. Key Features & Capabilities

### 4.1 Core business features

- Simple **product catalog** loaded from code.
- Creation of **orders** and **order line items**.
- Integration with **Stripe Checkout** (redirect-based).
- Order status lifecycle: `created` → `paid` → (optionally) `failed`.
- Display of **paid orders per user** on the UI home page.

### 4.2 Admin features

- Django admin `/admin/`:
  - View and filter `Order`, `OrderItem`, and `StripeEvent`.
  - Useful for debugging payment issues, reconciling orders, and manual inspection.
- Optional internal page:
  - `/debug/stripe-events/`: (if implemented) view of recent events and their linked orders.
- `/webhook-status/` endpoint and a small UI control (via navbar dropdown) to show:
  - Whether webhooks have been received.
  - The last webhook event type and received timestamp.

### 4.3 Security features

- Webhook endpoint verifies **Stripe signature** using `STRIPE_WEBHOOK_SECRET`.
- Webhook processing is **idempotent**:
  - `StripeEvent` stores event IDs; duplicates are ignored.
- Orders are always tied to **authenticated users** (via `request.user`).
- Sensitive Stripe keys are loaded from environment variables; not stored in code.

### 4.4 Integration points

- **Stripe Checkout**:
  - `stripe.checkout.Session.create(...)` used in a dedicated service function.
- **Stripe Webhooks**:
  - `/stripe/webhook/` receives events, validates them, and updates orders.
- Endpoint design enables **future frontends**:
  - `POST /api/checkout/` can be called by higher-level UI, mobile applications, or other services if needed.

---

## 5. Repository Structure

> This structure is indicative and may vary slightly based on the exact repository.


.
├── manage.py
├── .env.example                 # Sample environment configuration (no secrets)
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py              # Django + DB + Stripe configuration
│   ├── urls.py                  # Root URL routing
│   └── wsgi.py
└── store/
    ├── __init__.py
    ├── models.py                # Order, OrderItem, StripeEvent
    ├── views.py                 # Home page, webhook-status, debug views
    ├── urls.py                  # UI URLs
    ├── api/
    │   ├── __init__.py
    │   ├── serializers.py       # Checkout request serializer
    │   ├── views.py             # /api/checkout/ view
    │   └── urls.py              # API URLs
    ├── services/
    │   ├── products.py          # Product catalog definition
    │   ├── checkout.py          # High-level checkout orchestration
    │   ├── stripe.py            # Stripe API integration
    │   └── repositories/
    │       └── orders.py        # Order + OrderItem persistence functions
    ├── webhooks/
    │   ├── __init__.py
    │   ├── urls.py              # /stripe/webhook/ route
    │   └── views.py             # Stripe webhook handler
    ├── templates/
    │   ├── base.html
    │   └── store/
    │       ├── home.html
    │       └── debug_stripe_events.html
    └── static/
        └── store/
            └── app.js

---

### Where Things Live

- **Business domain models:** `store/models.py`

- **Business workflows:**
  - `store/services/checkout.py`
  - `store/repositories/orders.py`

- **Infrastructure integration (Stripe):**
  - `store/services/stripe.py`
  - `store/webhooks/views.py`

- **Configuration:**
  - `config/settings.py`
  - `.env` (local only; never commit)
  - `.env.example`

- **UI + API routing:**
  - `config/urls.py`
  - `store/urls.py`
  - `store/api/urls.py`
  - `store/webhooks/urls.py`

---

## 6. Environment Setup (Local Development)

### 6.1 Prerequisites

- Python 3.11+
- PostgreSQL (local or container)
- Stripe account (API keys + webhook secret)

**Optional**

- Stripe CLI (local webhook forwarding)
- virtualenv / pipenv

### 6.2 Python & virtual environment

---

# Create virtual env

python -m venv .venv

# Activate (Windows)

.venv\Scripts\activate

# Activate (macOS / Linux)

source .venv/bin/activate

### 6.3 Install dependencies

pip install -r requirements.txt

# or, if using pipenv:

# pipenv install

# pipenv shell

### 6.4 Environment variable setup

Create .env in the project root (same folder as manage.py), based on .env.example:
DEBUG=True
SECRET_KEY=django-insecure-local-dev-only
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=postgresql://ministore_user:YourPasswordHere@localhost:5432/ministore_checkout

STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

### 6.5 Local PostgreSQL setup

1. **Create a database user and DB (example):**
   CREATE USER ministore_user WITH PASSWORD 'YourPasswordHere';
   CREATE DATABASE ministore_checkout OWNER ministore_user;
   GRANT ALL PRIVILEGES ON DATABASE ministore_checkout TO ministore_user;

2. **Confirm DATABASE_URL points to this DB:-**

### 6.6 Running migrations

- python manage.py makemigrations --check --dry-run # Should show "No changes detected" once stable
- python manage.py migrate

### 6.7 Create a superuser (for admin access)

- python manage.py createsuperuser

# Follow prompts for username/email/password

### 6.8 Run the Server

- **python manage.py runserver**
- **UI:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/

## 7. Configuration & Secrets Management

### 7.1 Environment variables

#### Key environment variables:

- **Django**:
- DEBUG
- SECRET_KEY
- ALLOWED_HOSTS
- DATABASE_URL

- **Stripe**:
- STRIPE_PUBLIC_KEY
- STRIPE_SECRET_KEY
- STRIPE_WEBHOOK_SECRET

### 7.2 Secrets handling

- **Never commit .env with real secrets.**
- **For production:**
- Use secret managers (AWS Secrets Manager, GCP Secret Manager, Vault) or environment injections via CI/CD.
- Ensure SECRET_KEY is unique per environment and not guessable.
- Stripe live keys must be scoped and rotated according to security policy.

### 7.3 Different environments (dev / staging / prod)

- **Typical pattern:**
- .env.local / .env.development for local dev.
- .env.staging for test/staging environment (loaded by CI/CD).
- .env.production or secret manager for production.
- config/settings.py can be extended to support environment-specific overrides (e.g., DJANGO_SETTINGS_MODULE=config.settings.production).

### 7.4 Configuration best practices

- Fail fast if critical variables are missing (e.g., Stripe keys in production).
- Use DEBUG=False and strict ALLOWED_HOSTS in non-dev environments.
- Restrict database access (host firewall / security groups).
- Keep configuration immutable once deployed; use CI/CD pipelines to change it safely.

## 8. Database & Migrations

### 8.1 PostgreSQL usage

- Single PostgreSQL DB as primary data store.
- Tables created via Django migrations.
- No multi-tenant or sharding complexity in this minimal version.

### 8.2 Migration strategy

- Migrations live under store/migrations/ and django core apps.
- **General workflow:**
- Make model changes.
- Run python manage.py makemigrations.
- Review migration files into version control.
- Apply with python manage.py migrate in each environment.

### 8.3 Schema management

- **Models**:
- **Order** – tracks user, total amount, currency, Stripe IDs, timestamps, and status.
- **OrderItem** – links to Order, stores product info, unit price, and line totals.
- **StripeEvent** – stores event_id and minimal metadata for webhook idempotency.
- Fields are chosen to be stable and safe with stripe integration (`e.g., public_id as UUID for user-safe references`).

### 8.4 Data integrity considerations

- **Foreign keys**:
- OrderItem.order → Order.id (`on_delete=CASCADE`).
- **Uniqueness**:
- StripeEvent.event_id is unique to ensure idempotency.
- Stripe IDs on Order (`session + payment intent`) are unique where appropriate.
- **Order status transitions**:
- `mark_paid()` ensures second calls are idempotent.
- `mark_failed()` avoids modifying already-paid orders.

### 8.5 Backup / restore (high level)

- **Use standard PostgreSQL backup strategy:**
- pg_dump / pg_restore for logical backups.
- Managed DB snapshots if using cloud providers.
- Backup frequency should match business RPO (Recovery Point Objective).
- Always test restore into a non-production environment before relying on backup strategy.

## 9. API Documentation

### 9.1 Base URL (example)

- **Local:** http://127.0.0.1:8000/
- **API base:** http://127.0.0.1:8000/api/

### 9.2 Authentication method

- Currently uses Django session authentication:
- API requests assume the user is authenticated via standard Django login session.
- CSRF protection applies to unsafe methods.

### 9.3 API versioning

- For this minimal project, the API is unversioned (e.g., /api/checkout/).
- **For production-grade systems, consider:**
- /api/v1/checkout/ etc.
- Versioning via URL or header.

### 9.4 Example endpoint: POST /api/checkout/

**Request:**
{
"quantities": {
"product_key_1": 2,
"product_key_2": 1
}
}

- **Exact schema is defined in store/api/serializers.py and may vary, but conceptually:**
- quantities is a mapping of product identifiers to desired quantities.

**Response (success): -**
{
"checkout*url": "https://checkout.stripe.com/pay/cs_test*..."
}

**Response (not authenticated):**
{
"detail": "Authentication credentials were not provided."
}

**Error handling conventions:**

- Validation errors return 400 with DRF-standard structure.
- Unauthorized returns 401 / 403 as appropriate.
- Unexpected errors are surfaced as 500, and logs should contain technical detail.

## 10. Security Considerations

### 10.1 Authentication & authorization

- Uses Django’s built-in authentication system.
- Order.user ensures that orders are always tied to an authenticated user.
- Sensitive endpoints (checkout) require authentication.

### 10.2 CSRF / CORS

- CSRF protection remains enabled for session-based endpoints.
- The UI uses standard Django templates and forms, plus JS that includes CSRF appropriately.
- CORS is not configured for cross-origin APIs in this minimal version; if a separate SPA/mobile app is introduced, secure CORS settings must be added.

### 10.3 Data protection

- No card data or sensitive payment details are stored.
- Only opaque Stripe identifiers are persisted.
- **For production:**
- Use HTTPS everywhere.
- Encrypt data at rest (PostgreSQL-level / disk-level encryption).
- Consider encryption for sensitive PII if added in the future.

### 10.4 Secrets & key handling

- **Stripe keys and webhook secrets must be:**
- Environment-level secrets, not checked into git.
- Rotated per organization security policy.
- **Django SECRET_KEY must be:**
- Unique per environment.
- Treated as sensitive.

### 10.5 Audit / logging considerations

- **Logs should record:**
- Stripe webhook event IDs and types.
- Key status changes for Order objects.
- **For a production system, integrate with:**
- Centralized logging (ELK, CloudWatch, Stackdriver, etc.).
- SIEM / security monitoring as required.

## 11. Logging & Monitoring

### 11.1 Logging approach

- Use Django’s logging configuration in settings.py.
- **At minimum, log:**
- Stripe webhook verification failures.
- Webhook events that do not match any order.
- Unexpected exceptions in webhook or checkout flows.

### 11.2 Log levels

- INFO for normal lifecycle events (`received webhook`, `created order`).
- WARNING for suspicious or unexpected conditions (no matching order for event).
- ERROR for unhandled exceptions and critical failures.

### 11.3 Error tracking

- **Recommended to integrate with:**
- **Sentry, Rollbar, or similar for:**
- Exception aggregation.
- Environment tagging (`dev/stage/prod`).

### 11.4 Operational visibility

- **Define basic metrics (if monitoring is in scope):**
- Number of created / paid / failed orders.
- Webhook success / failure count.
- Stripe API error rate.

## 12. Testing Strategy

### 12.1 Unit tests

- **Focused on:**
- Services (`checkout`, `orders repository`).
- Model methods (`mark_paid`, `mark_failed`).
- Stripe integration wrapper (`mocked Stripe client`).

### 12.2 Integration tests

- **pytest with pytest-django used to:**
- Test /api/checkout/ end-to-end.
- Test webhook handling (`checkout.session.completed`) with realistic payloads.
- Assert idempotency of webhook processing.

### 12.3 How to run tests

- pytest # standard run
- pytest -q # quiet
- pytest -vv # verbose per-test output

### 12.4 Test coverage expectations

- **Critical flows should have tests:**
- Checkout requires auth.
- Checkout returns `checkout_url`.
- Webhook marks order as PAID and is idempotent.
- **For production-ready systems, aim for:**
- 80%+ coverage on core modules.
- 100% coverage on safety-critical functions (`idempotency`, `status transitions`).

## 13. Deployment Guide (High Level)

### 13.1 Supported environments

- **Development:** Local runserver + local PostgreSQL.
- **Staging/Production:** Any environment capable of:
- Running Python + Django.
- Connecting to PostgreSQL.
- Receiving HTTPS Stripe webhooks.

### 13.2 Deployment flow (example)

1. Build artifact (Docker image or packaged release).
2. **Apply database migrations:**
   python manage.py migrate

3. **Collect static files (if using):**
   python manage.py collectstatic

4. **Start app server:**

- gunicorn config.wsgi or
- uvicorn config.asgi (for ASGI stack).

5. Configure HTTPS and domain / load balancer.
6. Configure Stripe webhook endpoint in -- Stripe dashboard to point to:
   https://your-domain.com/stripe/webhook/

### 13.3 Required services

- PostgreSQL instance.
- Stripe account (test/live).
- Optional: log aggregation and monitoring service.

### 13.4 Pre-deployment checklist

- **DEBUG=False** in non-dev.
- **ALLOWED_HOSTS** configured.
- Database reachable and migrations applied.
- Stripe keys and webhook secret configured.
- Health check endpoint or basic / load test passes.

### 13.5 Post-deployment validation

- **Smoke test:**
- Login.
- Start checkout.
- Pay via Stripe.
- Confirm order visible as PAID.
- **Confirm webhooks:**
- Stripe dashboard shows successful webhook delivery.
- App logs show webhook processed without error.

## 14. Rollback & Recovery

### 14.1 Rollback strategy

- **Application rollback**:
- Deploy previous known-good version of the application.
- **Database rollback:**
- Ideally forward-only migrations with backup restore if needed.
- Avoid destructive migrations without backup.

### 14.2 DB rollback considerations

- Before applying schema changes:
- Take a DB snapshot or pg_dump.
- **For simple changes:**
- If migrations are reversible, python manage.py migrate app_name <migration_number> can roll back.
- **In production:**
- Plan for rolling forwards rather than complex rollbacks if user data is critical.

### 14.3 Disaster recovery overview

- Maintain regular backup schedule.
- Test restore into a non-production environment.
- Keep a documented runbook:
  -- How to restore DB from backup.
  -- How to reconfigure app to point to restored DB.

## 15. Contribution Guidelines (for Team)

### 15.1 Coding standards

- Follow PEP 8 for Python.
- Use type hints where practical.
- Keep functions and classes small and focused.
- Use the service layer for orchestration; avoid heavy views.

### 15.2 Branching strategy

- main / master: always deployable.
- dev / develop: integration branch (optional).
- Feature branches: feature/short-description.
- Bugfix branches: fix/short-description.

### 15.3 Pull Request (PR) process

- Every change should go via PR.
- **Include:**
- Problem statement.
- Summary of changes.
- Testing performed (with commands).
- Require at least one reviewer for merge.

### 15.4 Code review expectations

- Check correctness and edge cases.
- Ensure no secrets in diffs.
- **Check for:**
- Proper error handling.
- Logging of important events.
- No duplicated logic where a service exists.

```

```
