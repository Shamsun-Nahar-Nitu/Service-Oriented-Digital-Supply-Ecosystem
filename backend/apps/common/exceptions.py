"""
Uniform error response shape across the whole API.

Instead of every client having to guess whether an error is a flat dict,
a list, or a `detail` string, every error response looks like:

    {
        "success": false,
        "errors": {...}   # whatever DRF/validation produced
    }
"""

import logging

from rest_framework.views import exception_handler

logger = logging.getLogger("apps")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "success": False,
            "errors": response.data,
        }
        return response

    # Unhandled exception (500) - log it, DRF will let Django's default
    # error handling take over in production (DEBUG=False).
    logger.exception("Unhandled exception in %s", context.get("view"))
    return response
