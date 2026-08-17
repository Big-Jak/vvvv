import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",") if h.strip()]

# Vercel-specific: automatically trust the deployment's own domain, including
# preview deployments (which get a random *.vercel.app subdomain each time).
IS_VERCEL = os.getenv("VERCEL") == "1"
VERCEL_URL = os.getenv("VERCEL_URL")  # e.g. "my-app-abc123.vercel.app" (no scheme)
if IS_VERCEL:
    ALLOWED_HOSTS.append(".vercel.app")
    if VERCEL_URL and VERCEL_URL not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(VERCEL_URL)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1", "testserver") and not h.startswith(".")]
if IS_VERCEL:
    CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main.apps.MainConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

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

WSGI_APPLICATION = "project.wsgi.application"

import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=60,
        ssl_require=os.getenv("DATABASE_URL", "").startswith(("postgres://", "postgresql://")),
    )
}

# To use MySQL instead of SQLite, uncomment the following and comment out the above:
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": os.getenv("DB_NAME", "writing_feedback"),
#         "USER": os.getenv("DB_USER", "root"),
#         "PASSWORD": os.getenv("DB_PASSWORD", ""),
#         "HOST": os.getenv("DB_HOST", "localhost"),
#         "PORT": os.getenv("DB_PORT", "3306"),
#         "CONN_MAX_AGE": 60,
#         "ATOMIC_REQUESTS": True,
#         "OPTIONS": {
#             "charset": "utf8mb4",
#             "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "webmaster@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if not EMAIL_HOST or not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGIN_URL = "login"

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# On Vercel (and any other platform without persistent local disk), uploaded
# files must go to S3-compatible object storage instead of MEDIA_ROOT, since
# the local filesystem doesn't survive between requests. If AWS_STORAGE_BUCKET_NAME
# is set, switch the default file storage to S3; otherwise (e.g. local dev,
# Render with its persistent disk) fall back to the local filesystem as before.
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
if AWS_STORAGE_BUCKET_NAME:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "auto")
    # AWS_S3_ENDPOINT_URL lets this point at any S3-compatible provider
    # (e.g. Cloudflare R2, Backblaze B2) instead of AWS itself.
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL") or None
    AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN") or None
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}
else:
    STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage
