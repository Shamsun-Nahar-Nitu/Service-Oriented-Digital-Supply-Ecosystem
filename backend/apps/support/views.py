"""
Public FAQ chatbot endpoints.

Three things differ from the rest of the API on purpose:

- `AllowAny`. The project default is `IsAuthenticated` (see
  REST_FRAMEWORK in config/settings/base.py), but a support bot that only
  answers signed-in users is useless — most "how do I create an account"
  traffic is anonymous by definition.

- A dedicated throttle scope. The project default for anonymous callers is
  100/day, which a chat widget would burn through in one sitting. These
  views opt into the `faq-bot` scope instead (60/min), which still blocks
  scripted abuse without punishing a real conversation. Setting
  `throttle_classes` on the view replaces the defaults rather than
  stacking with them.

- No queryset. Nothing here touches the database; answers come from
  apps/support/data/faqs.csv via the cached index in faq_engine.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .faq_engine import answer_question, list_categories, list_faqs
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    FaqEntrySerializer,
)


class ChatView(APIView):
    """
    POST /api/v1/support/chat/

    Body: {"message": "how do I track my order"}
    Returns the best-matching FAQ answer, a confidence score, and up to
    three follow-up suggestions.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "faq-bot"

    @extend_schema(
        request=ChatRequestSerializer,
        responses={200: ChatResponseSerializer},
        summary="Ask the FAQ chatbot a question",
        tags=["support"],
    )
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = answer_question(serializer.validated_data["message"])
        return Response(result, status=status.HTTP_200_OK)


class FaqListView(APIView):
    """
    GET /api/v1/support/faqs/[?category=orders]

    The full FAQ list. The widget uses this to render starter chips so a
    customer has something to click instead of a blank input box.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "faq-bot"

    @extend_schema(
        responses={200: FaqEntrySerializer(many=True)},
        summary="List all FAQ entries",
        tags=["support"],
    )
    def get(self, request):
        category = request.query_params.get("category")
        return Response(list_faqs(category), status=status.HTTP_200_OK)


class FaqCategoryListView(APIView):
    """GET /api/v1/support/faq-categories/ — distinct categories, in file order."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "faq-bot"

    @extend_schema(summary="List FAQ categories", tags=["support"])
    def get(self, request):
        return Response({"categories": list_categories()}, status=status.HTTP_200_OK)
