"""
Global exception handler for the Academic ERP API.

All unhandled exceptions and DRF validation errors are funnelled through
``custom_exception_handler`` and returned as a consistent JSON envelope:

    {
        "error": "<human-readable message>",
        "code":  <HTTP status code>,
        "detail": <optional extra context>   # only present when useful
    }

Register in settings.py::

    REST_FRAMEWORK = {
        ...
        'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
    }
"""
import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    Throttled,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

logger = logging.getLogger(__name__)

# Human-readable fallback messages per status code
_STATUS_MESSAGES = {
    400: 'Bad request.',
    401: 'Authentication credentials were not provided or are invalid.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    405: 'Method not allowed.',
    429: 'Too many requests. Please slow down.',
    500: 'An unexpected server error occurred.',
}


def _build_response(message, code, detail=None):
    """Build the standard error envelope."""
    body = {'error': message, 'code': code}
    if detail is not None:
        body['detail'] = detail
    return Response(body, status=code)


def custom_exception_handler(exc, context):
    """
    Replace DRF's default exception handler with a consistent JSON envelope.

    Handles:
    - All DRF ``APIException`` subclasses (ValidationError, PermissionDenied, …)
    - Django's ``Http404``
    - Django's ``ValidationError`` (raised from model ``clean()`` methods)
    - Unexpected ``Exception`` — logged at ERROR level, returns 500

    Args:
        exc:     The exception instance.
        context: DRF context dict containing ``view`` and ``request``.

    Returns:
        ``Response`` with ``{"error": "...", "code": <int>}`` body.
    """
    # Let DRF normalise Http404 and PermissionDenied first
    response = exception_handler(exc, context)

    # ── DRF exceptions ────────────────────────────────────────────────────────
    if response is not None:
        code = response.status_code

        if isinstance(exc, ValidationError):
            # Flatten DRF validation errors into a readable string
            errors = response.data
            if isinstance(errors, dict):
                detail = {
                    field: msgs if isinstance(msgs, list) else [msgs]
                    for field, msgs in errors.items()
                }
                message = 'Validation failed.'
            elif isinstance(errors, list):
                detail = errors
                message = 'Validation failed.'
            else:
                detail = str(errors)
                message = str(errors)
            return _build_response(message, code, detail=detail)

        if isinstance(exc, NotAuthenticated):
            return _build_response(
                'Authentication credentials were not provided.', code
            )
        if isinstance(exc, AuthenticationFailed):
            return _build_response('Invalid or expired credentials.', code)
        if isinstance(exc, PermissionDenied):
            return _build_response(
                str(exc.detail) if exc.detail else _STATUS_MESSAGES[403], code
            )
        if isinstance(exc, NotFound):
            return _build_response(
                str(exc.detail) if exc.detail else _STATUS_MESSAGES[404], code
            )
        if isinstance(exc, MethodNotAllowed):
            return _build_response(
                f'Method "{exc.args[0] if exc.args else ""}" not allowed.', code
            )
        if isinstance(exc, Throttled):
            wait = getattr(exc, 'wait', None)
            msg = f'Too many requests. Retry in {wait:.0f}s.' if wait else _STATUS_MESSAGES[429]
            return _build_response(msg, code)

        # Generic DRF exception fallback
        message = _STATUS_MESSAGES.get(code, 'An error occurred.')
        return _build_response(message, code)

    # ── Django Http404 ────────────────────────────────────────────────────────
    if isinstance(exc, Http404):
        return _build_response(_STATUS_MESSAGES[404], status.HTTP_404_NOT_FOUND)

    # ── Django model ValidationError (from clean()) ───────────────────────────
    if isinstance(exc, DjangoValidationError):
        detail = exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
        return _build_response('Validation failed.', status.HTTP_400_BAD_REQUEST, detail=detail)

    # ── Unexpected exceptions ─────────────────────────────────────────────────
    logger.exception(
        'Unhandled exception in view %s: %s',
        context.get('view', 'unknown'),
        exc,
    )
    return _build_response(_STATUS_MESSAGES[500], status.HTTP_500_INTERNAL_SERVER_ERROR)
