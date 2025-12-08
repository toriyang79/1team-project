"""
Common app URL configuration
"""

from django.urls import path
from .api import LoginAPIView, RegisterAPIView, LogoutAPIView, MeAPIView

app_name = 'common'

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('me/', MeAPIView.as_view(), name='api_me'),
]
