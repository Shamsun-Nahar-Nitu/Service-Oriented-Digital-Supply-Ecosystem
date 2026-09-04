from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet

app_name = "transactions"

router = DefaultRouter()
router.register("", TransactionViewSet, basename="transaction")

urlpatterns = router.urls
