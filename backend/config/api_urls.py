"""
Aggregates every app's URLs under the /api/v1/ prefix.

Keeping this separate from config/urls.py means bumping to /api/v2/ later
(e.g. for a breaking change) is a one-line change, not a rewrite.
"""

from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.users.urls")),
    path("categories/", include("apps.categories.urls")),
    path("products/", include("apps.products.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("transactions/", include("apps.transactions.urls")),
    path("payments/", include("apps.payments.urls")),
]
