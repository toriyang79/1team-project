"""
User URLs
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserRegistrationView,
    UserProfileView,
    PasswordChangeView,
    AvatarUploadView,
    UserDeleteView,
    LogoutView
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Profile
    path('me/', UserProfileView.as_view(), name='profile'),
    path('me/password/', PasswordChangeView.as_view(), name='password_change'),
    path('me/avatar/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('me/delete/', UserDeleteView.as_view(), name='delete_account'),
]
