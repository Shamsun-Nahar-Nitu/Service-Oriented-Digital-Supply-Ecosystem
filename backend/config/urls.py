"""
Root URL configuration.

Everything the API exposes lives under /api/v1/, versioned so future
breaking changes can be introduced as /api/v2/ without disrupting existing
clients. Interactive API documentation (generated from the DRF views
themselves via drf-spectacular) is available at /api/docs/ (Swagger UI) and
/api/redoc/ (ReDoc).
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_v1_patterns = [
    path("auth/", include("apps.users.urls")),
    path("categories/", include("apps.category.urls")),
    path("products/", include("apps.products.urls")),
    path("inventory/", include("apps.inventory.urls")),
    path("transactions/", include("apps.transactions.urls")),
    path("payments/", include("apps.payments.urls")),
    path("support/", include("apps.support.urls")), 
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
    # OpenAPI schema + interactive docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
