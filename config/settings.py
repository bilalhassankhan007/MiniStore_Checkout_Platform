"""
Why this settings.py is designed this way:

- We load secrets (DB, Stripe keys) from .env so they never land in git.
- DATABASE_URL makes the project portable across environments.
- DRF is used only for the checkout endpoint (clean separation: UI page + API action).
- strip() on Stripe envs avoids invisible spaces that break webhook signature verification.
"""

from pathlib import Path

import environ

# ----------------------------
# Base directory
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# Environment (.env) loading
# ----------------------------
env = environ.Env(DEBUG=(bool, False))

# Read BASE_DIR/.env (project root)
# Why: keep local setup simple: clone -> create .env -> run.
environ.Env.read_env(BASE_DIR / ".env")

# ----------------------------
# Core settings
# ----------------------------
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# ----------------------------
# Timezone / Datetimes
# ----------------------------
# Why:
# - Store timestamps in UTC in the DB (best practice)
# - Display times in IST for your demo UI/admin
TIME_ZONE = "Asia/Kolkata"
USE_TZ = True

# Optional (nice for raw SQL / DB-side timestamps):
# This sets the PostgreSQL session timezone when Django connects.
DATABASES = {"default": env.db()}
DATABASES["default"].setdefault("OPTIONS", {})
DATABASES["default"]["OPTIONS"].setdefault("options", "-c timezone=Asia/Kolkata")

# ----------------------------
# Installed apps
# ----------------------------
INSTALLED_APPS = [
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    # Local
    "store",
]

# ----------------------------
# Middleware
# ----------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # Keep CSRF: we use session auth
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ----------------------------
# URLs / Templates
# ----------------------------
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Why: keep templates close to app while still allowing project-level override
        "DIRS": [BASE_DIR / "store" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ----------------------------
# DRF
# ----------------------------
REST_FRAMEWORK = {
    # Why: keep it simple. Session auth works with Django login + CSRF.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# ----------------------------
# Auth redirects
# ----------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ----------------------------
# Static files
# ----------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "store" / "static"]

# ----------------------------
# Stripe config (loaded from .env)
# IMPORTANT: strip() removes accidental leading space like " whsec_..."
# ----------------------------
STRIPE_PUBLIC_KEY = (env("STRIPE_PUBLIC_KEY", default="") or "").strip()
STRIPE_SECRET_KEY = (env("STRIPE_SECRET_KEY", default="") or "").strip()
STRIPE_WEBHOOK_SECRET = (env("STRIPE_WEBHOOK_SECRET", default="") or "").strip()

# ----------------------------
# Defaults
# ----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
