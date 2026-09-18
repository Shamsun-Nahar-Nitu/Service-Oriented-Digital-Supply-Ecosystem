from django.urls import path

from .views import (
    AdminDashboardView,
    AdminReportPDFView,
    ManagerDashboardView,
    ManagerReportPDFView,
    VendorDashboardView,
    VendorReportPDFView,
)

app_name = "finance"

urlpatterns = [
    path("dashboard/admin/", AdminDashboardView.as_view(), name="dashboard-admin"),
    path("dashboard/manager/", ManagerDashboardView.as_view(), name="dashboard-manager"),
    path("dashboard/vendor/", VendorDashboardView.as_view(), name="dashboard-vendor"),
    path("reports/admin/", AdminReportPDFView.as_view(), name="report-admin"),
    path("reports/manager/", ManagerReportPDFView.as_view(), name="report-manager"),
    path("reports/vendor/", VendorReportPDFView.as_view(), name="report-vendor"),
]
