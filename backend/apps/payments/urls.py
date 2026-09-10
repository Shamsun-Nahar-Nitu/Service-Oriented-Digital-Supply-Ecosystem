from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, SSLCommerzCallbackView

app_name = "payments"

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

urlpatterns = router.urls + [
	path("callback/<str:callback_type>/", SSLCommerzCallbackView.as_view(), name="callback"),
]
