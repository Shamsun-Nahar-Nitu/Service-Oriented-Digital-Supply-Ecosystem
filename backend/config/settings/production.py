"""Production settings — run with DJANGO_SETTINGS_MODULE=config.settings.production."""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS must be set explicitly via the
# environment in production; there is no wildcard fallback here on purpose.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Serve collected static files (Django admin CSS/JS) via WhiteNoise instead
# of a separate static file server.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
