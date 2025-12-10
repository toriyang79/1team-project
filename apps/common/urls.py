"""
Common app URL configuration
"""

from django.urls import path
from .api import (
    LoginAPIView,
    RegisterAPIView,
    LogoutAPIView,
    MeAPIView,
    SocialLoginAPIView,
    SocialCallbackAPIView
)

app_name = 'common'

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('register/', RegisterAPIView.as_view(), name='api_register'),
    path('logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('me/', MeAPIView.as_view(), name='api_me'),

    # 소셜 로그인
    path('social/<str:provider>/', SocialLoginAPIView.as_view(), name='social_login'),
    path('social/callback/<str:provider>/', SocialCallbackAPIView.as_view(), name='social_callback'),
]
