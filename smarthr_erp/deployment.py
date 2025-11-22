# smarthr_erp/deployment.py

from .settings import *
import os

# -----------------------
# DEBUG & SECURITY BASICS
# -----------------------

# Take DEBUG from env if present, otherwise fallback to whatever was in settings.py
DEBUG = os.environ.get("DEBUG", str(DEBUG)).lower() in ("true", "1", "yes")

# Secret key: prefer env, fallback to base settings
SECRET_KEY = os.environ.get("SECRET_KEY", SECRET_KEY)

# Allowed hosts – from env or sensible defaults (incl. Azure URL)
raw_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
if raw_hosts:
    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "ckppeoplesuite-cgasf7fzdre6c0c0.centralindia-01.azurewebsites.net",
    ]

# -----------------------
# STATIC FILES (WhiteNoise)
# -----------------------

wn = "whitenoise.middleware.WhiteNoiseMiddleware"
if wn not in MIDDLEWARE:
    MIDDLEWARE.insert(1, wn)

STATIC_ROOT = os.environ.get(
    "DJANGO_STATIC_ROOT",
    str(BASE_DIR / "staticfiles")
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -----------------------
# HTTPS / COOKIES
# -----------------------

if not DEBUG:
    # Production behind Azure reverse proxy
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Local/dev over plain HTTP
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# -----------------------
# EMAIL
# -----------------------

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", EMAIL_HOST_USER)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", EMAIL_HOST_PASSWORD)

# -----------------------
# CHANNELS / REDIS
# -----------------------

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}
