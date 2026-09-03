"""
Aggregates every app's URLs under the /api/ prefix.
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
