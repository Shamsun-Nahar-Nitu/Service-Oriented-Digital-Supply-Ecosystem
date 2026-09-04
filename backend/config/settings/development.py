"""Local development settings — run with DJANGO_SETTINGS_MODULE=config.settings.development."""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Convenient for local frontend work against any origin; production locks
# this down to an explicit CORS_ALLOWED_ORIGINS list instead.
CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS += ["django_extensions"] if env.bool("USE_DJANGO_EXTENSIONS", default=False) else []
