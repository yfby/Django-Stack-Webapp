"""Local classroom settings. Source, frontend and database have explicit homes."""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("FLOWDESK_DATA_DIR", BASE_DIR / "database" / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)


def local_key():
    key_file = DATA_DIR / ".development-key"
    try:
        fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return key_file.read_text(encoding="utf-8").strip()
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        key = secrets.token_urlsafe(48)
        stream.write(key)
    return key


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or ("" if os.environ.get("DJANGO_SETTINGS_MODULE") == "config.production" else local_key())
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [x.strip() for x in os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,[::1]"
).split(",") if x.strip()]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "database.apps.DatabaseConfig", "backend.workspace.apps.WorkspaceConfig", "backend.accounts.apps.AccountsConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "backend.workspace.middleware.WorkspaceMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "frontend" / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "backend.workspace.context_processors.workspace_context",
    ]},
}]
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3", "NAME": DATA_DIR / "flowdesk.sqlite3",
    # IMMEDIATE serializes writes to the JSON snapshots before reading them.
    "OPTIONS": {"timeout": 20, "transaction_mode": "IMMEDIATE"},
}}
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "frontend" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_FAILURE_VIEW = "backend.workspace.views.csrf_failure"
DATA_UPLOAD_MAX_MEMORY_SIZE = 128 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 128 * 1024
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
# PrintPilot account settings
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "workspace:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
EMAIL_BACKEND = os.environ.get("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "PrintPilot <noreply@example.com>")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1") == "1"
EMAIL_TIMEOUT = 10
AUTH_USER_MODEL = "accounts.User"
PASSWORD_RESET_TIMEOUT = 3600
