from pathlib import Path
from datetime import timedelta
from decouple import config
import os

try:
    import redis
except ImportError:
    redis = None

BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================
# CORE SETTINGS
# =============================================
"""
CORE SETTINGS: Fundamental Django configurations.
- SECRET_KEY: Used for cryptographic signing (CSRF, sessions). Must stay secret in production.
- DEBUG: Shows detailed error pages when True. Must be False in production.
- ALLOWED_HOSTS: Domain names/IPs Django will serve. Prevents Host header attacks.
- PRODUCTION: Master switch — forces DEBUG=False and DJANGO_DEV=False.
- DJANGO_DEV: Enables dev-only behaviors (insecure cookies, all CORS origins, local Redis).
"""
SECRET_KEY = config("SECRET_KEY")

PRODUCTION = config("PRODUCTION", default=False, cast=bool)
DJANGO_DEV = config("DJANGO_DEV", default=False, cast=bool)
DEBUG = config("DEBUG", default=True, cast=bool)

if PRODUCTION:
    DEBUG = False
    DJANGO_DEV = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

print(f"🔧 CORE SETTINGS: PRODUCTION={PRODUCTION}, DEBUG={DEBUG}, DJANGO_DEV={DJANGO_DEV}")
print(f"🔧 ALLOWED_HOSTS: {ALLOWED_HOSTS}")


# =============================================
# INSTALLED APPS
# =============================================
"""
INSTALLED APPS: All active Django apps in this project.
- Django Core: Admin, auth, sessions, messages, static files.
- Third Party:
    * django_prometheus: Exposes /metrics endpoint for Prometheus monitoring.
    * rest_framework: Django REST Framework for building APIs.
    * drf_yasg: Auto-generates Swagger/OpenAPI documentation.
    * corsheaders: Handles Cross-Origin Resource Sharing for frontend access.
    * django_filters: Enables field-level filtering on API list endpoints.
- Custom Apps: Medihub-specific apps for authentication, profiles, blog, posts, location.
"""
INSTALLED_APPS = [
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third Party
    "rest_framework",
    "drf_yasg",
    "corsheaders",
    "django_filters",

    # Custom Apps
    "authentication",
    "location",
    "medihub",
    "profiles",
    "blog",
    "post",
]

AUTH_USER_MODEL = "authentication.User"
print("✅ INSTALLED APPS: Loaded all Django, third-party, and custom Medihub apps")


# =============================================
# MIDDLEWARE
# =============================================
"""
MIDDLEWARE: Request/response processors that run in order for every request.
- PrometheusBeforeMiddleware / PrometheusAfterMiddleware: Wraps all requests for metrics.
- RequestIdMiddleware: Attaches a unique ID to each request for tracing/logging.
- SecurityMiddleware: Adds security headers (HSTS, X-Content-Type, etc.).
- CorsMiddleware: Must be placed high — handles CORS preflight requests.
- SessionMiddleware: Manages user sessions.
- CsrfViewMiddleware: Protects against Cross-Site Request Forgery attacks.
- AuthenticationMiddleware: Attaches the authenticated user to each request.
- MessageMiddleware: Handles one-time flash messages.
- XFrameOptionsMiddleware: Prevents clickjacking via iframe embedding.
"""
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "request_id.middleware.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]
print("✅ MIDDLEWARE: Prometheus, security, CORS, sessions, authentication configured")


# =============================================
# URL & TEMPLATES
# =============================================
"""
URL & TEMPLATES: URL routing and HTML template rendering configuration.
- ROOT_URLCONF: Entry point for all URL routing (medihub/urls.py).
- TEMPLATES: Tells Django where to find HTML templates and how to render them.
- Context processors: Inject variables into every template automatically
  (e.g., request object, authenticated user, messages).
"""
ROOT_URLCONF = "medihub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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
print("✅ URL & TEMPLATES: Routing and template configuration loaded")


# =============================================
# WSGI APPLICATION
# =============================================
"""
WSGI: Web Server Gateway Interface — entry point for HTTP requests.
- Used by Gunicorn in production to serve the Django app.
- Handles all standard HTTP requests (REST API calls, admin panel, etc.).
"""
WSGI_APPLICATION = "medihub.wsgi.application"
print("✅ WSGI: Application gateway configured")


# =============================================
# PROXY & SECURITY SETTINGS (Nginx)
# =============================================
"""
PROXY & SECURITY: Configures Django to work correctly behind Nginx reverse proxy.

- SECURE_PROXY_SSL_HEADER: Tells Django the request came over HTTPS (forwarded by Nginx).
- USE_X_FORWARDED_HOST: Reads real hostname from X-Forwarded-Host header set by Nginx.
- USE_X_FORWARDED_PORT: Reads real port from X-Forwarded-Port header.

Cookie Security:
- CSRF_COOKIE_SAMESITE / SESSION_COOKIE_SAMESITE = "Lax": Prevents CSRF while
  allowing normal browser navigation.
- SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE: Cookies only sent over HTTPS.
  Disabled in DJANGO_DEV so local HTTP dev server works without SSL.
- SECURE_SSL_REDIRECT = False: Nginx handles SSL termination, not Django.
"""
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

if DJANGO_DEV:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = False  # Nginx handles SSL, not Django

print("🔒 PROXY & SECURITY: SSL handled by Nginx, cookie security configured")


# =============================================
# PASSWORD VALIDATION
# =============================================
"""
PASSWORD VALIDATION: Enforces strong passwords on registration and password change.
- UserAttributeSimilarityValidator: Blocks passwords similar to username/email.
- MinimumLengthValidator: Requires at least 9 characters.
- CommonPasswordValidator: Blocks common passwords like "password123".
- NumericPasswordValidator: Prevents all-numeric passwords like "12345678".
"""
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 9}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
print("✅ PASSWORD VALIDATION: Min 9 chars, no common/numeric-only passwords")


# =============================================
# DATABASE CONFIGURATION
# =============================================
"""
DATABASE: PostgreSQL configuration for Medihub.
- ENGINE: PostgreSQL — robust, multi-user, production-ready.
- NAME/USER/PASSWORD: Loaded from environment variables (never hardcode credentials).
- HOST: "db" is the Docker Compose service name for the database container.
- PORT: Default PostgreSQL port 5432.

Always set these via environment variables or Docker secrets in production.
"""
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="medihub"),
        "USER": config("POSTGRES_USER", default="medihub_user"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="medihub_pass"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}
print(f"📊 DATABASE: PostgreSQL → {config('POSTGRES_DB', default='medihub')} @ {config('DB_HOST', default='db')}")


# =============================================
# REDIS CONFIGURATION
# =============================================
"""
REDIS: In-memory data store used for caching and channel layers.

DJANGO_DEV=True (Local Development):
  - Connects to localhost:6380 (local Redis instance).
  - No password required.

DJANGO_DEV=False (Production):
  - Connects to "redis" Docker container on port 6379.
  - Supports password auth via REDIS_PASSWORD env var.

_build_redis_url(): Builds the Redis connection URL with optional password.
USE_REDIS_CACHE: Auto-detects Redis availability with a 2-second timeout.
  Falls back to in-memory cache if Redis is unreachable.
"""
if DJANGO_DEV:
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = config("REDIS_LOCAL_PORT", default=6380, cast=int)
    REDIS_DB = 0
    REDIS_PASSWORD = ""
    print(f"🔴 REDIS: Connecting to localhost:{REDIS_PORT} (dev)")
else:
    REDIS_HOST = config("REDIS_HOST", default="redis")
    REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
    REDIS_DB = config("REDIS_DB", default=0, cast=int)
    REDIS_PASSWORD = config("REDIS_PASSWORD", default="")
    print(f"🔴 REDIS: Connecting to {REDIS_HOST}:{REDIS_PORT} (production)")


def _build_redis_url():
    if REDIS_PASSWORD:
        return f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    return f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


REDIS_URL = _build_redis_url()

USE_REDIS_CACHE = False
if redis:
    try:
        _r = redis.StrictRedis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
            password=REDIS_PASSWORD or None, socket_connect_timeout=2,
        )
        _r.ping()
        USE_REDIS_CACHE = True
        print(f"✅ REDIS: Connected to {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"⚠️  REDIS: Connection failed, falling back to in-memory cache ({str(e)[:50]})")
else:
    print("⚠️  REDIS: Module not installed, using in-memory cache")


# =============================================
# CACHE CONFIGURATION
# =============================================
"""
CACHE: Where Django stores cached data (OTPs, rate limits, sessions, API responses).

Redis available (USE_REDIS_CACHE=True):
  - django-redis backend — shared across all app instances, persists across restarts.
  - Ideal for production with multiple servers or containers.

Redis unavailable (USE_REDIS_CACHE=False):
  - LocMemCache — stored in application memory, lost on restart, not shared.
  - Suitable for single-server development only.
"""
if USE_REDIS_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
    print("💾 CACHE: Using Redis (distributed, persistent)")
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "medihub-local-cache",
        }
    }
    print("💾 CACHE: Using LocMemCache (in-memory, non-persistent)")


# =============================================
# REST FRAMEWORK
# =============================================
"""
REST FRAMEWORK: Django REST Framework (DRF) configuration.

Authentication:
  - JWTAuthentication: Stateless token auth via Authorization: Bearer <token> header.

Permissions:
  - AllowAny by default — individual views override with stricter permissions.

Throttling (Rate Limiting) — protects against abuse:
  - anon: 100 req/hour for unauthenticated users.
  - user: 1000 req/hour for authenticated users.
  - login: 5 req/min — prevents brute force attacks.
  - signup: 3 req/hour — prevents spam registrations.
  - otp: 10 req/hour — prevents OTP flooding.
  - password_reset: 5 req/hour — prevents abuse.

Filtering:
  - DjangoFilterBackend: ?field=value filtering on list endpoints.
  - SearchFilter: ?search=query full-text search.
  - OrderingFilter: ?ordering=field result ordering.
"""
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
        "login_user": "5/min",
        "login_anon": "5/min",
        "signup_user": "3/hour",
        "signup_anon": "3/hour",
        "otp": "10/hour",
        "password_reset": "5/hour",
    },
}
print("🔐 REST FRAMEWORK: JWT auth, rate limiting, and filtering configured")


# =============================================
# SWAGGER SETTINGS
# =============================================
"""
SWAGGER: Auto-generated interactive API documentation (accessible at /api/docs/).

- SECURITY_DEFINITIONS: Configures JWT Bearer token auth in Swagger UI.
  Users paste their JWT token → Swagger sends it as: Authorization: Bearer <token>
- USE_SESSION_AUTH: Disabled — we use JWT, not Django session auth.

Swagger UI lets developers:
  - Browse all API endpoints with descriptions.
  - Test endpoints directly from the browser.
  - See request/response schemas and examples.
"""
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": 'JWT Authorization. Format: "Bearer <token>"',
        }
    },
    "USE_SESSION_AUTH": False,
}
print("📚 SWAGGER: API docs configured with JWT Bearer authentication")


# =============================================
# CORS SETTINGS
# =============================================
"""
CORS: Cross-Origin Resource Sharing — allows the frontend to call this API
from a different domain/port (e.g., React on localhost:5173 → Django on localhost:8000).

- CORS_ALLOW_CREDENTIALS: Allows cookies and auth headers in cross-origin requests.
- CORS_ALLOW_HEADERS: Explicitly whitelisted request headers.

DJANGO_DEV=True:
  - CORS_ALLOW_ALL_ORIGINS=True — accepts requests from any origin (dev convenience).

DJANGO_DEV=False (Production):
  - CORS_ALLOWED_ORIGINS: Restricted list loaded from env var.
  - CSRF_TRUSTED_ORIGINS: Origins trusted for CSRF-protected POST requests.
  In production, set these to your actual frontend domain(s).
"""
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept", "accept-encoding", "authorization", "content-type",
    "dnt", "origin", "user-agent", "x-csrftoken", "x-requested-with",
]

if DJANGO_DEV:
    CORS_ALLOW_ALL_ORIGINS = True
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000", "http://localhost:3000",
        "http://localhost:5173", "http://127.0.0.1:3000",
    ]
    print("🌐 CORS: Allow All Origins (DJANGO_DEV mode)")
else:
    CORS_ALLOWED_ORIGINS = config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8000",
        cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
    )
    CSRF_TRUSTED_ORIGINS = config(
        "CSRF_TRUSTED_ORIGINS",
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8000",
        cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
    )
    print(f"🌐 CORS: {len(CORS_ALLOWED_ORIGINS)} allowed origins")
    print(f"🌐 CSRF: {len(CSRF_TRUSTED_ORIGINS)} trusted origins")


# =============================================
# JWT CONFIGURATION
# =============================================
"""
JWT: JSON Web Token settings for stateless authentication.

ACCESS_TOKEN:
  - Short-lived token sent in every API request header: Authorization: Bearer <token>
  - Lifetime: ACCESS_TOKEN_DAYS env var (default 60 days).

REFRESH_TOKEN:
  - Long-lived token used to obtain a new access token when it expires.
  - Lifetime: REFRESH_TOKEN_DAYS env var (default 60 days).

ROTATE_REFRESH_TOKENS=True:
  - Every refresh call issues a brand new refresh token.
  - Limits token reuse and improves security.

BLACKLIST_AFTER_ROTATION=True:
  - Old refresh tokens are blacklisted after rotation.
  - Prevents replay attacks using stolen old tokens.

AUTH_HEADER_TYPES = ("Bearer",):
  - Token must be sent as: Authorization: Bearer <token>
"""
ACCESS_TOKEN_DAYS = config("ACCESS_TOKEN_DAYS", default=60, cast=int)
REFRESH_TOKEN_DAYS = config("REFRESH_TOKEN_DAYS", default=60, cast=int)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=ACCESS_TOKEN_DAYS),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_TOKEN_DAYS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
print(f"🔑 JWT: Access={ACCESS_TOKEN_DAYS}d, Refresh={REFRESH_TOKEN_DAYS}d, rotation+blacklist enabled")


# =============================================
# EMAIL CONFIGURATION
# =============================================
"""
EMAIL: Settings for sending transactional emails (OTP, password reset, notifications).

EMAIL_BACKEND:
  - console.EmailBackend (default): Prints emails to terminal — for development only.
  - smtp.EmailBackend: Sends real emails via SMTP — set this in production.

SMTP Settings:
  - EMAIL_HOST: SMTP server address (e.g., smtp.gmail.com).
  - EMAIL_PORT: 587 for STARTTLS, 465 for SSL.
  - EMAIL_USE_TLS: Encrypts the SMTP connection.
  - EMAIL_HOST_USER / EMAIL_HOST_PASSWORD: SMTP login credentials.
    For Gmail, use an App Password (not your account password).

OTP_EXPIRE_TIME: How long OTP codes remain valid in seconds (default: 300s = 5 min).
"""
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
OTP_EXPIRE_TIME = config("OTP_EXPIRE_TIME", default=300, cast=int)

print(f"📧 EMAIL: Backend={EMAIL_BACKEND.split('.')[-2]}, OTP expires in {OTP_EXPIRE_TIME}s")


# =============================================
# INTERNATIONALIZATION
# =============================================
"""
INTERNATIONALIZATION: Language and timezone support.

- LANGUAGE_CODE: Default language for the app (en-us = English).
- TIME_ZONE: Default timezone — Asia/Dhaka for Bangladesh.
- USE_I18N: Enables Django's translation framework (multi-language support).
- USE_TZ: Stores all datetimes in UTC in the database.
  Django converts to TIME_ZONE when displaying to users.
  Always keep True to avoid timezone-related bugs.
"""
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True
print(f"🌍 INTERNATIONALIZATION: Language={LANGUAGE_CODE}, Timezone={TIME_ZONE}")


# =============================================
# CUSTOM USER MODEL & AUTO FIELD
# =============================================
"""
CUSTOM USER MODEL:
- AUTH_USER_MODEL = "authentication.User": Uses a custom User model from the
  authentication app instead of Django's default User.
  Enables email-based login, custom fields, and custom methods.
  MUST be set before running the first migration.

DEFAULT_AUTO_FIELD:
- BigAutoField: Uses 64-bit integer primary keys instead of 32-bit.
  Supports up to 9.2 quintillion rows — future-proof for large datasets.
  Recommended for all new Django projects.
"""
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
print("👤 CUSTOM USER MODEL: authentication.User with BigAutoField PKs")


# =============================================
# STATIC & MEDIA FILES
# =============================================
"""
STATIC FILES: CSS, JavaScript, images bundled with the app (not user-uploaded).
- STATIC_URL: URL prefix browsers use to request static files (/static/...).
- STATIC_ROOT: Directory where `collectstatic` gathers all static files.
  Nginx serves this directory directly in production (bypasses Django for speed).

MEDIA FILES: User-uploaded content (profile pictures, documents, etc.).
- MEDIA_URL: URL prefix for accessing uploaded files (/media/...).
- MEDIA_ROOT: Local filesystem directory where uploads are stored.
  In production, Nginx serves /media/ directly from this directory.

Run `python manage.py collectstatic` before deploying to populate STATIC_ROOT.
"""
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
print(f"📁 STATIC: {STATIC_ROOT}")
print(f"📸 MEDIA: {MEDIA_ROOT}")


# =============================================
# FIREBASE PUSH NOTIFICATIONS
# =============================================
"""
FIREBASE: Push notification support for mobile apps (iOS/Android) via FCM.

FIREBASE_CREDENTIALS_PATH: Path to the Firebase service account JSON file.
  - Download from: Firebase Console → Project Settings → Service Accounts.
  - Contains private keys — never commit to version control.
  - Set path via FIREBASE_CREDENTIALS_PATH env var.

Initialization behavior:
  - File exists → Firebase initialized, push notifications enabled.
  - File missing → Firebase skipped gracefully, app still works normally.

Used for:
  - Push notifications to mobile apps
  - Real-time alerts and messaging
  - Device token management
"""
FIREBASE_CREDENTIALS_PATH = config("FIREBASE_CREDENTIALS_PATH", default="firebase-key.json")

if os.path.exists(FIREBASE_CREDENTIALS_PATH):
    try:
        import firebase_admin
        from firebase_admin import credentials as fb_credentials
        _cred = fb_credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(_cred)
        print("🔥 FIREBASE: Push notifications initialized successfully")
    except Exception as e:
        print(f"❌ FIREBASE: Initialization failed — {str(e)[:60]}")
else:
    print(f"⚠️  FIREBASE: No credentials at '{FIREBASE_CREDENTIALS_PATH}' — push notifications disabled")


# =============================================
# LOGGING
# =============================================
"""
LOGGING: Structured JSON logging for Medihub.

- disable_existing_loggers=False: Keeps Django's built-in loggers active.
- formatters.json: Outputs structured JSON logs using python-json-logger.
  Includes: timestamp, log level, logger name, message.
  JSON format integrates with log aggregators (ELK Stack, CloudWatch, Grafana Loki).
- handlers.console: Streams logs to stdout/stderr.
  Docker/Kubernetes captures stdout and forwards to log aggregators automatically.
- root level=INFO: Captures INFO, WARNING, ERROR, CRITICAL across all loggers.
  Change to DEBUG for verbose output during development.

Log levels (ascending severity):
  DEBUG → INFO → WARNING → ERROR → CRITICAL
"""
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
print("📋 LOGGING: Structured JSON logging to console at INFO level")


# =============================================
# CELERY & RABBITMQ
# =============================================
RABBITMQ_USER = config("RABBITMQ_DEFAULT_USER", default="medihub")
RABBITMQ_PASS = config("RABBITMQ_DEFAULT_PASS", default="medihub")
RABBITMQ_HOST = config("RABBITMQ_HOST", default="rabbitmq")
RABBITMQ_PORT = config("RABBITMQ_PORT", default="5672")

CELERY_BROKER_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_EXTENDED = True

# beat
CELERY_BEAT_SCHEDULE = {
    "beat-health-check-every-30s": {
        "task": "medihub.tasks.beat_health_check",
        "schedule": 30.0,
    },
    "beat-log-active-users-every-60s": {
        "task": "medihub.tasks.beat_log_active_users",
        "schedule": 60.0,
    },
    "beat-cleanup-expired-otps-every-5m": {
        "task": "medihub.tasks.beat_cleanup_expired_otps",
        "schedule": 300.0,
    },
    "beat-system-ping-every-10s": {
        "task": "medihub.tasks.beat_system_ping",
        "schedule": 10.0,
    },
    # "beat-system-email-send-me": {
    #     "task": "medihub.tasks.send_me_email_everyminute",
    #     "schedule": 60.0,
    # },
    
    
}
print(f"🐇 CELERY: Broker=RabbitMQ@{RABBITMQ_HOST}, Backend=Redis")


print("\n" + "=" * 60)
print("✅ MEDIHUB SETTINGS LOADED SUCCESSFULLY")
print("=" * 60 + "\n")
