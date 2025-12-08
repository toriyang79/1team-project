"""
Custom exception handlers for DRF
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data
        custom_response = {
            'error': True,
            'message': str(exc),
            'details': response.data,
            'status_code': response.status_code
        }
        response.data = custom_response

        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)} "
            f"[{context['request'].method} {context['request'].path}]"
        )
    else:
        # Handle non-DRF exceptions
        logger.error(
            f"Unhandled Exception: {exc.__class__.__name__} - {str(exc)} "
            f"[{context['request'].method} {context['request'].path}]",
            exc_info=True
        )
        response = Response(
            {
                'error': True,
                'message': 'Internal server error',
                'details': str(exc),
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
