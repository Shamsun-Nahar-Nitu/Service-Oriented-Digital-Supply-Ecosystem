"""
Root URL configuration.

Everything the outside world talks to is versioned under /api/v1/. Django
admin is kept at /admin/ purely as an internal ops tool. API documentation
is auto-generated from the DRF viewsets/serializers via drf-spectacular and
served as Swagger UI at /api/docs/.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Versioned API
    path("api/v1/", include("project.api_urls")),

    # OpenAPI schema + docs UIs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
