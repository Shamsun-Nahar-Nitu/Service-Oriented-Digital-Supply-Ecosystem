from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsAdminOrManager, IsVendor

from .reports import build_admin_report_pdf, build_manager_report_pdf, build_vendor_report_pdf
from .services import DashboardAnalyticsService, resolve_date_range, resolve_granularity

RANGE_PARAMS = [
    OpenApiParameter(
        "period", OpenApiTypes.STR,
        description="today|7d|30d|90d|12m|this_month|last_month|all. Defaults to 30d.",
    ),
    OpenApiParameter(
        "start", OpenApiTypes.DATE, description="Explicit range start (YYYY-MM-DD), overrides period."
    ),
    OpenApiParameter(
        "end", OpenApiTypes.DATE, description="Explicit range end (YYYY-MM-DD), overrides period."
    ),
    OpenApiParameter(
        "granularity", OpenApiTypes.STR,
        description="day|month for the time series. Auto-chosen from the range if omitted.",
    ),
]


def _service_from_request(request):
    start, end = resolve_date_range(request.query_params)
    granularity = resolve_granularity(request.query_params, start, end)
    return DashboardAnalyticsService(start=start, end=end, granularity=granularity)


def _pdf_response(pdf_bytes, filename):
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class AdminDashboardView(APIView):
    """GET /api/v1/finance/dashboard/admin/ — platform-wide revenue and commission KPIs."""

    permission_classes = [IsAdmin]

    @extend_schema(parameters=RANGE_PARAMS, responses=OpenApiTypes.OBJECT, tags=["finance"])
    def get(self, request):
        return Response(_service_from_request(request).admin_summary())


class ManagerDashboardView(APIView):
    """GET /api/v1/finance/dashboard/manager/ — vendor and customer monitoring."""

    permission_classes = [IsAdminOrManager]

    @extend_schema(parameters=RANGE_PARAMS, responses=OpenApiTypes.OBJECT, tags=["finance"])
    def get(self, request):
        return Response(_service_from_request(request).manager_summary())


class VendorDashboardView(APIView):
    """GET /api/v1/finance/dashboard/vendor/ — the signed-in vendor's own performance."""

    permission_classes = [IsVendor]

    @extend_schema(parameters=RANGE_PARAMS, responses=OpenApiTypes.OBJECT, tags=["finance"])
    def get(self, request):
        return Response(_service_from_request(request).vendor_summary(request.user))


class AdminReportPDFView(APIView):
    """GET /api/v1/finance/reports/admin/ — downloadable PDF of the admin dashboard."""

    permission_classes = [IsAdmin]

    @extend_schema(parameters=RANGE_PARAMS, responses={200: OpenApiTypes.BINARY}, tags=["finance"])
    def get(self, request):
        summary = _service_from_request(request).admin_summary()
        return _pdf_response(build_admin_report_pdf(summary), "admin-report.pdf")


class ManagerReportPDFView(APIView):
    """GET /api/v1/finance/reports/manager/ — downloadable PDF of the manager dashboard."""

    permission_classes = [IsAdminOrManager]

    @extend_schema(parameters=RANGE_PARAMS, responses={200: OpenApiTypes.BINARY}, tags=["finance"])
    def get(self, request):
        summary = _service_from_request(request).manager_summary()
        return _pdf_response(build_manager_report_pdf(summary), "manager-report.pdf")


class VendorReportPDFView(APIView):
    """GET /api/v1/finance/reports/vendor/ — downloadable PDF of the vendor's own dashboard."""

    permission_classes = [IsVendor]

    @extend_schema(parameters=RANGE_PARAMS, responses={200: OpenApiTypes.BINARY}, tags=["finance"])
    def get(self, request):
        summary = _service_from_request(request).vendor_summary(request.user)
        return _pdf_response(build_vendor_report_pdf(summary, request.user), "vendor-report.pdf")
