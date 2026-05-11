# 🇧🇩 Django Settings.py — সম্পূর্ণ বাংলা ব্যাখ্যা
### দার্শনিক ও তাত্ত্বিক বিশ্লেষণসহ

---

> **এই ফাইলটি কী?**
> `settings.py` হলো একটি Django প্রজেক্টের **মস্তিষ্ক** — এখানেই সব কনফিগারেশন থাকে। ঠিক যেমন একটি মানুষের DNA তে তার শরীরের সব নির্দেশনা থাকে, তেমনি `settings.py`-তে পুরো অ্যাপ্লিকেশনের আচরণ নির্ধারিত হয়।

---

## ১. প্রাথমিক Import ও Path Setup

```python
from pathlib import Path
from datetime import timedelta
from decouple import config
import os

try:
    import redis
except ImportError:
    redis = None

BASE_DIR = Path(__file__).resolve().parent.parent
```

### প্রতিটি লাইনের ব্যাখ্যা:

**`from pathlib import Path`**
- `pathlib` হলো Python-এর built-in লাইব্রেরি যা file system path নিয়ে কাজ করে।
- আগে `os.path.join()` দিয়ে path বানাতে হতো, এটি তার আধুনিক বিকল্প।
- **না থাকলে কী হবে?** `BASE_DIR` বানানো যাবে না, ফলে `STATIC_ROOT`, `MEDIA_ROOT` সব ভেঙে পড়বে।

**`from datetime import timedelta`**
- JWT token-এর মেয়াদ নির্ধারণ করতে ব্যবহার হয় (যেমন: ৬০ দিন)।
- **না থাকলে কী হবে?** `SIMPLE_JWT` settings-এ `timedelta(days=60)` লেখা যাবে না, Token মেয়াদ সেট হবে না।

**`from decouple import config`**
- `python-decouple` লাইব্রেরি। `.env` ফাইল বা environment variable থেকে sensitive তথ্য (password, secret key) পড়ে আনে।
- **দার্শনিক দিক:** "Separation of Concerns" — কোড আর configuration আলাদা রাখো। Secret key কখনো codebase-এ থাকা উচিত নয়।
- **না থাকলে কী হবে?** Secret key সরাসরি কোডে লিখতে হবে → GitHub-এ push হলে হ্যাকারদের জন্য দরজা খুলে যাবে।

**`try: import redis / except ImportError: redis = None`**
- Redis লাইব্রেরি available কিনা gracefully check করে।
- **না থাকলে কী হবে?** Redis না থাকলে `ImportError` উঠে app crash করবে। এই pattern টি defensive programming-এর উদাহরণ।

**`BASE_DIR = Path(__file__).resolve().parent.parent`**
- `__file__` = বর্তমান ফাইলের path (`settings.py`)
- `.resolve()` = absolute path বানায়
- `.parent.parent` = দুই লেভেল উপরে যায় → project root পায়
- **না থাকলে কী হবে?** `templates`, `static`, `media` folder খুঁজে পাবে না।

---

## ২. Core Settings (মূল সেটিংস)

```python
SECRET_KEY = config("SECRET_KEY")
PRODUCTION = config("PRODUCTION", default=False, cast=bool)
DJANGO_DEV = config("DJANGO_DEV", default=False, cast=bool)
DEBUG = config("DEBUG", default=True, cast=bool)

if PRODUCTION:
    DEBUG = False
    DJANGO_DEV = False
```

### তাত্ত্বিক ব্যাখ্যা:

**`SECRET_KEY`**
- Django-র সবচেয়ে গুরুত্বপূর্ণ variable। এটি দিয়ে:
  - CSRF token তৈরি হয়
  - Session data sign হয়
  - Password reset link তৈরি হয়
- **দার্শনিক দিক:** এটি একটি অ্যাপ্লিকেশনের "আত্মা" — যতক্ষণ এটি গোপন আছে, ততক্ষণ সব নিরাপদ।
- **না থাকলে কী হবে?** `ImproperlyConfigured` error। App চালুই হবে না।
- **ফাঁস হলে কী হবে?** হ্যাকার fake session তৈরি করতে পারবে, CSRF bypass করতে পারবে।

**`PRODUCTION` flag**
- Production মানে real server যেখানে real user আছে।
- এই flag `True` হলে automatically `DEBUG=False` হয়ে যায়।
- **দার্শনিক দিক:** Production-এ কোনো ভুলের জায়গা নেই। এটি একটি safety net।

**`DJANGO_DEV` flag**
- Local development-এ কিছু restriction শিথিল করে (যেমন: CORS সব origin allow করে)।
- **না থাকলে কী হবে?** Developer localhost-এ কাজ করতে পারবে না কারণ CORS block করবে।

**`DEBUG = True/False`**
- `DEBUG=True`: Error হলে সুন্দর HTML page দেখায়, কোডের কোথায় error সেটাও দেখায়।
- `DEBUG=False`: Error হলে শুধু generic "500 Server Error" দেখায়।
- **দার্শনিক দিক:** Development-এ transparency দরকার, Production-এ security দরকার।
- **Production-এ `DEBUG=True` রাখলে কী হবে?** হ্যাকার আপনার পুরো code structure, database credentials, installed packages সব দেখতে পাবে। **এটি catastrophic।**

**`ALLOWED_HOSTS`**
- Django শুধু এই domain/IP থেকে আসা request accept করবে।
- **না থাকলে কী হবে?** "Host header attack" — হ্যাকার fake Host header পাঠিয়ে আপনার server-কে ভুল domain-এ redirect করাতে পারে।
- **Production-এ `*` রাখলে কী হবে?** যেকোনো domain থেকে request আসবে — নিরাপত্তা শূন্য।

---

## ৩. Installed Apps

```python
INSTALLED_APPS = [
    "django_prometheus",
    "django.contrib.admin",
    ...
    "authentication",
    "location",
    "medihub",
    "profiles",
    "blog",
    "post",
]
```

### প্রতিটি App-এর ব্যাখ্যা:

**`django_prometheus`**
- Server-এর health metrics expose করে `/metrics` endpoint-এ।
- Prometheus সেই data collect করে, Grafana তা visualize করে।
- **না থাকলে কী হবে?** Server কেমন চলছে, কতটা load আছে — কিছুই জানা যাবে না।

**`django.contrib.admin`**
- Built-in admin panel `/admin/`।
- Database-এর সব data graphical UI দিয়ে manage করা যায়।
- **না থাকলে কী হবে?** Admin panel কাজ করবে না।

**`django.contrib.auth`**
- User authentication system — login, logout, permission।
- **না থাকলে কী হবে?** কোনো user management থাকবে না।

**`django.contrib.contenttypes`**
- Generic relation system — একটি model অন্য যেকোনো model-এর সাথে relate করতে পারে।
- **না থাকলে কী হবে?** `auth` app কাজ করবে না, permissions ভাঙবে।

**`django.contrib.sessions`**
- User session manage করে।
- **না থাকলে কী হবে?** Login state save হবে না।

**`rest_framework`**
- Django REST Framework — API বানানোর জন্য।
- **না থাকলে কী হবে?** কোনো API endpoint কাজ করবে না।

**`drf_yasg`**
- Auto-generate করে Swagger UI → `/api/docs/`।
- **না থাকলে কী হবে?** API documentation থাকবে না, frontend developer বুঝবে না কোন endpoint কীভাবে call করতে হয়।

**`corsheaders`**
- CORS headers handle করে।
- **না থাকলে কী হবে?** Browser থেকে API call block হবে। Frontend কাজ করবে না।

**`django_filters`**
- API list endpoint-এ `?field=value` filter করা যায়।
- **না থাকলে কী হবে?** সব data এক সাথে আসবে, filter করা যাবে না।

**Custom Apps (authentication, location, medihub, profiles, blog, post)**
- এগুলো Medihub-এর নিজস্ব features।
- **না থাকলে কী হবে?** সেই feature-এর models, views, urls কিছুই কাজ করবে না।

**`AUTH_USER_MODEL = "authentication.User"`**
- Django-কে বলছে: default `User` model ব্যবহার না করে `authentication` app-এর custom `User` model ব্যবহার কর।
- **দার্শনিক দিক:** Default User model-এ username দিয়ে login হয়, কিন্তু আমরা email দিয়ে login করতে চাই।
- **না থাকলে কী হবে?** Custom fields (phone, profile pic) add করা যাবে না। **এই setting প্রথম migration-এর আগেই সেট করতে হবে, পরে পরিবর্তন করলে database ভেঙে যায়।**

---

## ৪. Middleware

```python
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "request_id.middleware.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    ...
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]
```

### Middleware কী?

**দার্শনিক ব্যাখ্যা:** Middleware হলো একটি request-এর "যাত্রাপথের চেকপোস্ট"। প্রতিটি request Django-তে ঢোকার সময় এবং বের হওয়ার সময় এই middlewares-এর মধ্য দিয়ে যায়।

```
Browser → [Prometheus] → [RequestId] → [Security] → [CORS] → [Session] → [CSRF] → [Auth] → View
View → [Auth] → [CSRF] → [Session] → [CORS] → [Security] → [RequestId] → [Prometheus] → Browser
```

**`PrometheusBeforeMiddleware` ও `PrometheusAfterMiddleware`**
- Request শুরু ও শেষে metrics record করে।
- **অবস্থান গুরুত্বপূর্ণ:** Before সবার আগে, After সবার শেষে — তাহলেই পুরো request time measure হয়।
- **না থাকলে কী হবে?** Monitoring dashboard-এ কোনো data আসবে না।

**`RequestIdMiddleware`**
- প্রতিটি request-কে একটি unique ID দেয় (যেমন: `req-a1b2c3d4`)।
- Log-এ এই ID দিয়ে trace করা যায়: "৩ টার সময় error কোন request-এ হয়েছিল?"
- **না থাকলে কী হবে?** Production log-এ হাজারো request-এর মধ্যে specific একটি খুঁজে পাওয়া অসম্ভব।

**`SecurityMiddleware`**
- HTTP security headers add করে:
  - `X-Content-Type-Options: nosniff` — browser-কে file type guess করতে দেয় না
  - `X-XSS-Protection` — XSS attack থেকে রক্ষা করে
- **না থাকলে কী হবে?** Browser-level attacks-এর বিরুদ্ধে কোনো রক্ষা থাকবে না।

**`CorsMiddleware`**
- **অবশ্যই `SessionMiddleware`-এর আগে থাকতে হবে।**
- CORS preflight request handle করে।
- **না থাকলে কী হবে?** Frontend থেকে API call করলে browser block করবে।

**`CsrfViewMiddleware`**
- প্রতিটি POST/PUT/DELETE request-এ CSRF token verify করে।
- **দার্শনিক দিক:** এটি প্রমাণ করে যে request টি আসলেই আপনার সাইট থেকে এসেছে, অন্য কোনো evil site থেকে নয়।
- **না থাকলে কী হবে?** কোনো evil website আপনার logged-in user-এর হয়ে form submit করতে পারবে (CSRF attack)।

**`AuthenticationMiddleware`**
- প্রতিটি request-এ `request.user` set করে।
- **না থাকলে কী হবে?** View-এ `request.user` পাওয়া যাবে না। কে login করেছে জানা যাবে না।

---

## ৫. URL ও Templates

```python
ROOT_URLCONF = "medihub.urls"
TEMPLATES = [...]
```

**`ROOT_URLCONF`**
- Django-কে বলছে: সব URL `medihub/urls.py` থেকে শুরু কর।
- **না থাকলে কী হবে?** `ImproperlyConfigured` error। কোনো URL কাজ করবে না।

**`TEMPLATES`**
- Django কোথায় HTML template খুঁজবে এবং কীভাবে render করবে সেটা বলে।
- `APP_DIRS=True` মানে প্রতিটি app-এর `templates/` folder-এ খুঁজবে।
- **Context processors:** প্রতিটি template-এ automatically কিছু variable inject করে:
  - `request` — current HTTP request
  - `user` — logged-in user
  - `messages` — flash messages

---

## ৬. WSGI Application

```python
WSGI_APPLICATION = "medihub.wsgi.application"
```

- WSGI = Web Server Gateway Interface।
- Production-এ Gunicorn এই entry point দিয়ে Django app চালায়।
- **দার্শনিক দিক:** এটি Django-র "দরজা" — বাইরের web server (Nginx/Gunicorn) এই দরজা দিয়েই ঢোকে।
- **না থাকলে কী হবে?** Gunicorn app খুঁজে পাবে না। Production deployment fail হবে।

---

## ৭. Proxy ও Security (Nginx-এর জন্য)

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

SESSION_COOKIE_SECURE = True  # (non-dev)
CSRF_COOKIE_SECURE = True     # (non-dev)
SECURE_SSL_REDIRECT = False   # Nginx handles this
```

### আর্কিটেকচার বোঝা দরকার:

```
User Browser
    ↓ HTTPS
[Nginx] ← SSL terminate করে এখানেই
    ↓ HTTP (internal)
[Django/Gunicorn]
```

**`SECURE_PROXY_SSL_HEADER`**
- Nginx Django-কে বলে: "আমি HTTPS-এ এসেছিলাম"।
- Django নিজে SSL দেখতে পায় না (কারণ সে HTTP-তে কথা বলছে Nginx-এর সাথে)।
- **না থাকলে কী হবে?** Django মনে করবে সব request HTTP-তে আসছে → `request.is_secure()` সব সময় `False` হবে।

**`SESSION_COOKIE_SECURE = True`**
- Browser শুধু HTTPS connection-এ session cookie পাঠাবে।
- **না থাকলে কী হবে?** HTTP-তেও cookie যাবে → man-in-the-middle attack-এ cookie চুরি হতে পারে।

**`CSRF_COOKIE_SECURE = True`**
- CSRF cookie শুধু HTTPS-এ যাবে।
- **না থাকলে কী হবে?** CSRF protection দুর্বল হয়ে যায়।

**`SECURE_SSL_REDIRECT = False`**
- Django নিজে HTTP → HTTPS redirect করবে না (Nginx করবে)।
- **কেন?** Nginx অনেক বেশি efficient এই কাজে। Django দিয়ে করালে unnecessary overhead হয়।

---

## ৮. Password Validation

```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "...UserAttributeSimilarityValidator"},
    {"NAME": "...MinimumLengthValidator", "OPTIONS": {"min_length": 9}},
    {"NAME": "...CommonPasswordValidator"},
    {"NAME": "...NumericPasswordValidator"},
]
```

**`UserAttributeSimilarityValidator`**
- Password যদি username বা email-এর মতো হয় তাহলে reject করে।
- **না থাকলে কী হবে?** User `john@gmail.com` → password `john123` রাখতে পারবে। সহজেই guess করা যাবে।

**`MinimumLengthValidator` (min_length=9)**
- কমপক্ষে ৯ character-এর password লাগবে।
- **দার্শনিক দিক:** প্রতিটি extra character brute force attack-কে exponentially কঠিন করে।
- **না থাকলে কী হবে?** User `abc` password রাখতে পারবে।

**`CommonPasswordValidator`**
- "password", "123456789", "qwerty" ইত্যাদি reject করে।
- **না থাকলে কী হবে?** হ্যাকার common password list দিয়ে সহজেই crack করতে পারবে।

**`NumericPasswordValidator`**
- শুধু সংখ্যার password (যেমন: `123456789`) reject করে।
- **না থাকলে কী হবে?** সহজে guessable numeric password ব্যবহার করা যাবে।

---

## ৯. Database Configuration

```python
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
```

**`ENGINE: postgresql`**
- PostgreSQL ব্যবহার করা হচ্ছে।
- SQLite-এর চেয়ে কেন ভালো? Concurrent users, transactions, ACID compliance, JSON support।
- **দার্শনিক দিক:** Database choice হলো foundation। ভুল choice করলে পরে migration nightmare।

**`HOST: "db"`**
- Docker Compose-এ database container-এর নাম "db"।
- Docker internal network-এ "db" hostname resolve হয় database container-এর IP-তে।
- **না থাকলে কী হবে?** Database connection fail হবে।

**Credentials from config()**
- Password hardcode না করে environment variable থেকে পড়া।
- **না থাকলে কী হবে?** GitHub-এ push করলে সবাই database password দেখতে পাবে।

---

## ১০. Redis Configuration

```python
if DJANGO_DEV:
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = config("REDIS_LOCAL_PORT", default=6380, cast=int)
else:
    REDIS_HOST = config("REDIS_HOST", default="redis")
    REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
```

**Redis কী?**
- In-memory key-value store। অত্যন্ত দ্রুত (microseconds)।
- ব্যবহার: Cache, Session, OTP store, Rate limiting।

**Dev-এ `6380`, Production-এ `6379` কেন?**
- Dev machine-এ locally installed Redis চলে `6380`-তে।
- Production Docker-এ Redis container চলে `6379`-তে।

**`_r.ping()` দিয়ে connection test**
- Settings load হওয়ার সময়ই Redis available কিনা check করে।
- **না থাকলে কী হবে?** Runtime-এ cache write করতে গিয়ে error হবে।

**Graceful Fallback**
- Redis না থাকলে in-memory cache use করে। App crash করে না।
- **দার্শনিক দিক:** "Fail gracefully" — একটি component fail করলে পুরো system না থেমে degraded mode-এ চলুক।

---

## ১১. Cache Configuration

```python
if USE_REDIS_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            ...
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            ...
        }
    }
```

**Redis Cache**
- Multiple server instance-এর মধ্যে shared।
- Server restart-এ data থাকে।
- OTP, rate limit counter সব এখানে।
- **না থাকলে কী হবে?** Multiple instance deploy করলে একটির cache অন্যটি দেখতে পাবে না → OTP মিলবে না।

**LocMemCache**
- Single process-এর memory-তে।
- Restart-এ সব মুছে যায়।
- Development-এর জন্য ঠিক আছে।
- **Production-এ use করলে কী হবে?** OTP cache হারিয়ে যাবে, rate limiting কাজ করবে না।

---

## ১২. REST Framework

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "login_user": "5/min",
        "signup_anon": "3/hour",
        "otp": "10/hour",
        ...
    },
}
```

**`JWTAuthentication`**
- প্রতিটি request-এ `Authorization: Bearer <token>` header check করে।
- JWT = JSON Web Token। Stateless — server-এ কিছু store করতে হয় না।
- **দার্শনিক দিক:** Session-based auth-এ server-কে "মনে রাখতে" হয়। JWT-তে token নিজেই proof।
- **না থাকলে কী হবে?** Token check হবে না, যেকোনো request authenticated মনে করবে।

**`AllowAny` (default permission)**
- সব endpoint default-এ public।
- **কেন?** প্রতিটি view নিজে permission declare করবে — explicit করা ভালো।
- **না থাকলে কী হবে?** যদি `IsAuthenticated` default হয়, তাহলে login endpoint-ও blocked হবে!

**Throttling (Rate Limiting):**

| Key | Rate | উদ্দেশ্য |
|-----|------|---------|
| `anon` | 100/hour | সাধারণ anonymous request |
| `user` | 1000/hour | Authenticated user |
| `login_user` | 5/min | Brute force protection |
| `signup_anon` | 3/hour | Spam registration রোধ |
| `otp` | 10/hour | OTP flood রোধ |
| `password_reset` | 5/hour | Abuse রোধ |

**না থাকলে কী হবে?** হ্যাকার লাখো login attempt করতে পারবে (brute force), হাজারো fake account বানাতে পারবে, OTP system overwhelm করতে পারবে।

---

## ১৩. Swagger Settings

```python
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
    "USE_SESSION_AUTH": False,
}
```

- `/api/docs/` URL-এ interactive API documentation দেখায়।
- Developer JWT token paste করে সরাসরি browser থেকে API test করতে পারে।
- **না থাকলে কী হবে?** Documentation নেই → Frontend developer জানবে না কোন endpoint কী করে → Team collaboration ভেঙে পড়বে।

---

## ১৪. CORS Settings

```python
CORS_ALLOW_CREDENTIALS = True

if DJANGO_DEV:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", ...)
    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", ...)
```

**CORS কী?**
- Browser security policy: একটি domain-এর JavaScript অন্য domain-এর API call করতে পারবে কিনা।
- `frontend.com` থেকে `api.medihub.com`-এ call করলে — CORS check হবে।

**`CORS_ALLOW_CREDENTIALS = True`**
- Cookie এবং Authorization header সহ cross-origin request allow।
- **না থাকলে কী হবে?** JWT token header-এ পাঠানো যাবে না।

**Dev-এ `CORS_ALLOW_ALL_ORIGINS = True`**
- যেকোনো origin থেকে request আসতে পারবে।
- **Production-এ এটি করলে কী হবে?** যেকোনো evil website আপনার API call করতে পারবে।

**Production-এ specific origins**
- শুধু registered frontend domain-গুলো থেকে request accept।
- **না থাকলে কী হবে?** Frontend একদম কাজ করবে না (browser block করবে)।

---

## ১৫. JWT Configuration

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=60),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

**Access Token vs Refresh Token:**

```
User logs in
    ↓
Server দেয়: Access Token (৬০ দিন) + Refresh Token (৬০ দিন)
    ↓
User API call করে: Authorization: Bearer <access_token>
    ↓
Access Token expire হলে:
    ↓
Refresh Token দিয়ে নতুন Access Token নেয়
```

**`ROTATE_REFRESH_TOKENS = True`**
- প্রতিবার refresh করলে নতুন refresh token দেয়, পুরনোটা invalid হয়।
- **না থাকলে কী হবে?** Refresh token চুরি হলে সে indefinitely নতুন access token নিতে পারবে।

**`BLACKLIST_AFTER_ROTATION = True`**
- পুরনো refresh token-কে blacklist-এ রাখে।
- **না থাকলে কী হবে?** চুরি যাওয়া old token দিয়ে replay attack করা যাবে।

**৬০ দিনের lifetime কেন?**
- সাধারণত access token ১৫ মিনিট বা ১ ঘণ্টা হয়। এখানে ৬০ দিন রাখা হয়েছে — এটি একটি ডিজাইন সিদ্ধান্ত। বেশি দিন হলে চুরি হলে বেশিক্ষণ misuse হতে পারে।

---

## ১৬. Email Configuration

```python
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
OTP_EXPIRE_TIME = config("OTP_EXPIRE_TIME", default=300, cast=int)
```

**`console.EmailBackend` (default)**
- Development-এ email পাঠানোর বদলে terminal-এ print করে।
- **না থাকলে কী হবে?** Dev-এ real SMTP configure না করলে email feature test করা যাবে না অথবা real email চলে যাবে।

**`EMAIL_USE_TLS = True`**
- SMTP connection encrypt করে।
- **না থাকলে কী হবে?** Email credential plain text-এ network দিয়ে যাবে — সহজে sniff করা যাবে।

**`OTP_EXPIRE_TIME = 300`**
- OTP ৫ মিনিট পর expire হয়।
- **না থাকলে কী হবে?** OTP কখনো expire না হলে, পুরনো OTP দিয়ে পরেও login করা যাবে।

---

## ১৭. Internationalization

```python
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True
```

**`TIME_ZONE = "Asia/Dhaka"`**
- Admin panel-এ, log-এ সময় Dhaka timezone-এ দেখাবে।

**`USE_TZ = True`**
- Database-এ সব time UTC-তে store হবে।
- Django display করার সময় `TIME_ZONE` অনুযায়ী convert করবে।
- **দার্শনিক দিক:** UTC হলো সত্য — timezone হলো interpretation। Internally সত্য রাখো, প্রদর্শনীতে interpret করো।
- **না থাকলে কী হবে?** Daylight saving time, timezone migration-এ time calculation ভুল হবে। এটি debugging nightmare।

---

## ১৮. Custom User Model ও Auto Field

```python
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

**`BigAutoField`**
- Primary key হিসেবে 64-bit integer ব্যবহার করে।
- সর্বোচ্চ ৯.২ quintillion rows support করে।
- **না থাকলে কী হবে (32-bit)?** ২.১ billion rows-এর পর ID overflow হবে → database corrupt হবে। বড় platform-এর জন্য এটি real risk।

---

## ১৯. Static ও Media Files

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

**Production Architecture:**
```
Browser requests /static/app.js
    ↓
Nginx directly serves from STATIC_ROOT (Django bypass করে)
    → দ্রুত, efficient

Browser requests /media/profile_pic.jpg
    ↓
Nginx directly serves from MEDIA_ROOT
    → দ্রুত, Django load হয় না
```

**`collectstatic`**
- `python manage.py collectstatic` চালালে সব app-এর static file `STATIC_ROOT`-এ copy হয়।
- **না চালালে কী হবে?** Production-এ CSS/JS/images পাওয়া যাবে না। App ugly দেখাবে।

---

## ২০. Firebase Push Notifications

```python
FIREBASE_CREDENTIALS_PATH = config("FIREBASE_CREDENTIALS_PATH", default="firebase-key.json")

if os.path.exists(FIREBASE_CREDENTIALS_PATH):
    try:
        firebase_admin.initialize_app(_cred)
    except Exception as e:
        print(f"❌ FIREBASE: Initialization failed — {str(e)[:60]}")
else:
    print(f"⚠️  FIREBASE: No credentials — push notifications disabled")
```

**Graceful Degradation:**
- Firebase file না থাকলে quietly skip করে।
- App crash করে না।
- **দার্শনিক দিক:** Optional feature না থাকলে core functionality বন্ধ হওয়া উচিত নয়।
- **`firebase-key.json` GitHub-এ push করলে কী হবে?** Firebase project সম্পূর্ণ compromise হবে।

---

## ২১. Logging

```python
LOGGING = {
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
```

**কেন JSON logging?**
- Machine-readable format।
- ELK Stack (Elasticsearch + Logstash + Kibana) সহজে parse করতে পারে।
- Log aggregator tools এই format পছন্দ করে।

**`level: INFO`**
- INFO, WARNING, ERROR, CRITICAL সব log হবে।
- DEBUG log হবে না (খুব verbose)।
- **Production-এ `DEBUG` level রাখলে কী হবে?** লাখো debug log → disk full, performance slow, sensitive data log-এ চলে যেতে পারে।

**Log Levels:**
```
DEBUG    → বিস্তারিত developer info
INFO     → সাধারণ events ("User logged in")
WARNING  → অস্বাভাবিক কিন্তু চলছে ("Redis slow")
ERROR    → কিছু fail করেছে ("Email send failed")
CRITICAL → System ভাঙছে ("Database down")
```

---

## 📊 সামগ্রিক Architecture চিত্র

```
Internet
    ↓
[Nginx] — SSL terminate, static files serve
    ↓
[Gunicorn + Django]
    ↓              ↓              ↓
[PostgreSQL]   [Redis]     [Firebase FCM]
  (data)       (cache)      (notifications)
    ↓
[Prometheus] ← metrics
    ↓
[Grafana] ← visualization
```

---

## 🔑 সবচেয়ে গুরুত্বপূর্ণ বিষয়গুলো (Summary)

| Setting | Production-এ ভুল করলে |
|---------|----------------------|
| `DEBUG=True` | পুরো codebase exposed |
| `SECRET_KEY` hardcode | সব security broken |
| `ALLOWED_HOSTS=*` | Host header attack |
| `SESSION_COOKIE_SECURE=False` | Cookie hijacking |
| `AUTH_USER_MODEL` পরে change | Database migration nightmare |
| `USE_TZ=False` | Timezone bugs |
| Firebase key GitHub-এ | Firebase compromised |
| Rate limiting বন্ধ | Brute force attack |

---

> **শেষ কথা:** একটি ভালো `settings.py` শুধু "কাজ করে" না — এটি নিরাপদ, maintainable, এবং environment-aware হয়। এই settings file টি সেই তিনটি গুণই ধারণ করে।
