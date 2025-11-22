from .settings import *
import os

# Production mode
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1")

# Security
SECRET_KEY = os.environ.get("SECRET_KEY", SECRET_KEY)
# deployment.py
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# WhiteNoise for static files — insert only if not already present
wn = "whitenoise.middleware.WhiteNoiseMiddleware"
if wn not in MIDDLEWARE:
    MIDDLEWARE.insert(1, wn)

STATIC_ROOT = os.environ.get(
    "DJANGO_STATIC_ROOT",
    str(BASE_DIR / "staticfiles")
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# SSL (Azure reverse proxy)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email (Prod)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", EMAIL_HOST_USER)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", EMAIL_HOST_PASSWORD)

# Channels Redis (Production)
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [REDIS_URL]},
    }
}
