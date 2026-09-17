from rest_framework import serializers

from .faq_engine import MAX_QUERY_CHARS


class ChatRequestSerializer(serializers.Serializer):
    """Validates the inbound customer message."""

    message = serializers.CharField(
        max_length=MAX_QUERY_CHARS,
        trim_whitespace=True,
        allow_blank=False,
        help_text="The customer's question, in their own words.",
    )


class ChatResponseSerializer(serializers.Serializer):
    """Shape of the bot reply. Declared so drf-spectacular documents it."""

    matched = serializers.BooleanField()
    confidence = serializers.FloatField()
    answer = serializers.CharField()
    matched_question = serializers.CharField(allow_blank=True)
    category = serializers.CharField(allow_blank=True)
    suggestions = serializers.ListField(child=serializers.CharField())


class FaqEntrySerializer(serializers.Serializer):
    id = serializers.CharField()
    category = serializers.CharField()
    question = serializers.CharField()
    answer = serializers.CharField()
