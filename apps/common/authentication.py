"""
Custom authentication classes
"""

from rest_framework import authentication, exceptions
from django.utils import timezone
from apps.users.models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    API Key based authentication for public tokens

    Usage:
        X-API-Key: your-api-key-here
    """
    keyword = 'X-API-Key'

    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')

        if not api_key:
            return None

        try:
            key_obj = APIKey.objects.select_related('user').get(key=api_key)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key')

        if not key_obj.is_valid():
            raise exceptions.AuthenticationFailed('API Key is inactive or expired')

        # Update last used timestamp
        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])

        return (key_obj.user, key_obj)

    def authenticate_header(self, request):
        return self.keyword
