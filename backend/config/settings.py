"""
Django settings for the multi-vendor backend.

Every value that changes between environments (local dev, Docker,
production) is read from an environment variable via python-decouple,
never hardcoded — the same .env file feeds Docker Compose and Django,
so they can't drift out of sync with each other.
"""

from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from decouple import Csv, config

# backend/config/settings.py -> parents[1] == backend/
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())


# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    # first-party — one Django "app" per feature domain, matching db/schema.sql section-for-section.
    "apps.users",
    "apps.vendors",
    "apps.categories",
    "apps.products",
    "apps.inventory",
    "apps.cart",
    "apps.wishlist",
    "apps.coupons",
    "apps.orders",
    "apps.shipping",
    "apps.reviews",
    "apps.commission",
    "apps.payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # CorsMiddleware must load before CommonMiddleware (django-cors-headers'
    # own requirement) so preflight OPTIONS requests get CORS headers
    # attached before Common's URL-rewriting logic runs.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        # Only django.contrib.admin actually renders templates in this
        # API-only project — DRF's browsable API also needs this backend.
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------
# Database — MySQL, matching db/schema.sql
# ---------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
# Points Django at our own model instead of the built-in one — required
# because the built-in User has a `username` field we don't want; we
# log in with email (see apps/users/models/user.py).
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------
# Static / media
# ---------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Locked down by default — every new endpoint requires login unless
    # a view explicitly opts out with AllowAny (e.g. register, login).
    # Safer default than the other way around.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Issues a new refresh token on every refresh call ("refresh token
    # rotation") so a stolen refresh token has a short shelf life.
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,  # would need rest_framework_simplejwt.token_blacklist app — deferred
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ---------------------------------------------------------------------
# CORS — the React dev server runs on a different origin than the API
# ---------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS", default="http://localhost:5173", cast=Csv()
)


# ---------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# What the celery_beat container (docker-compose.yml) actually runs —
# generates the previous week's vendor payouts every Monday at 02:00.
# See apps.commission.tasks.generate_last_weeks_payouts for why this
# can't just schedule generate_vendor_payouts directly with static args.
CELERY_BEAT_SCHEDULE = {
    "generate-weekly-vendor-payouts": {
        "task": "apps.commission.tasks.generate_last_weeks_payouts",
        "schedule": crontab(day_of_week="monday", hour=2, minute=0),
    },
}


# ---------------------------------------------------------------------
# Razorpay
# ---------------------------------------------------------------------
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = config("RAZORPAY_KEY_SECRET", default="")
RAZORPAY_WEBHOOK_SECRET = config("RAZORPAY_WEBHOOK_SECRET", default="")
