import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler so every error response — validation
    errors, auth failures, 404s, throttling, uncaught exceptions — has the
    same shape:

        {
            "success": false,
            "status_code": 400,
            "errors": {...}
        }

    This makes the API predictable for any frontend consuming it, instead of
    each error type having its own ad-hoc payload shape.
    """
    if isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)

    if response is not None:
        response.data = {
            "success": False,
            "status_code": response.status_code,
            "errors": response.data,
        }
        return response

    # Unhandled exception: log it and return a generic 500 instead of
    # leaking a stack trace to the client.
    logger.exception("Unhandled exception in %s", context.get("view"))
    return Response(
        {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "errors": {"detail": "An unexpected error occurred. Please try again later."},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
