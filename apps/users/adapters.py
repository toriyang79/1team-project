"""
Custom adapters for django-allauth
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter
    """
    def get_login_redirect_url(self, request):
        return settings.LOGIN_REDIRECT_URL


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter
    """
    def pre_social_login(self, request, sociallogin):
        """
        소셜 로그인 전처리
        이미 존재하는 이메일로 소셜 로그인 시 자동 연결
        """
        # 이메일이 이미 존재하는 경우 자동으로 연결
        if sociallogin.is_existing:
            return

        if 'email' not in sociallogin.account.extra_data:
            return

        try:
            email = sociallogin.account.extra_data['email'].lower()
            from apps.users.models import User
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """
        소셜 로그인으로 회원가입 시 사용자 정보 자동 설정
        """
        user = super().populate_user(request, sociallogin, data)

        # 닉네임 자동 생성 (provider 이름 + 난수)
        if not user.nickname:
            import uuid
            provider = sociallogin.account.provider
            user.nickname = f"{provider}_{uuid.uuid4().hex[:8]}"

        return user
