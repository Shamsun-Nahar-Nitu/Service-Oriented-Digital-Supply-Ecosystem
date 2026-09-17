from django.urls import path

from .views import ChatView, FaqCategoryListView, FaqListView

app_name = "support"

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("faqs/", FaqListView.as_view(), name="faq-list"),
    path("faq-categories/", FaqCategoryListView.as_view(), name="faq-category-list"),
]
