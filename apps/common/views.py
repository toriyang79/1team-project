"""
Common views
"""

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from apps.users.models import User, APIKey


class DashboardView(TemplateView):
    """
    Dashboard home page
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get statistics
        context['total_users'] = User.objects.count()
        context['total_api_keys'] = APIKey.objects.filter(is_active=True).count()

        return context


class LoginView(View):
    """
    Login page
    """
    template_name = 'login.html'

    def get(self, request):
        # 이미 로그인된 사용자는 대시보드로 리다이렉트
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # 사용자 인증
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # 로그인 상태 유지 설정
            if not remember_me:
                request.session.set_expiry(0)  # 브라우저 종료 시 세션 만료

            messages.success(request, f'{user.nickname}님, 환영합니다!')
            return redirect('/')
        else:
            messages.error(request, '이메일 또는 비밀번호가 올바르지 않습니다.')
            return render(request, self.template_name)


class RegisterView(View):
    """
    Register page
    """
    template_name = 'register.html'

    def get(self, request):
        # 이미 로그인된 사용자는 대시보드로 리다이렉트
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        terms = request.POST.get('terms')

        # 유효성 검사
        if not terms:
            messages.error(request, '이용약관에 동의해주세요.')
            return render(request, self.template_name)

        if password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, self.template_name)

        # 이메일 중복 확인
        if User.objects.filter(email=email).exists():
            messages.error(request, '이미 사용 중인 이메일입니다.')
            return render(request, self.template_name)

        # 닉네임 중복 확인
        if User.objects.filter(nickname=nickname).exists():
            messages.error(request, '이미 사용 중인 닉네임입니다.')
            return render(request, self.template_name)

        try:
            # 사용자 생성
            user = User.objects.create_user(
                email=email,
                password=password,
                nickname=nickname
            )

            # 자동 로그인 (백엔드 명시)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'{user.nickname}님, 회원가입을 환영합니다!')
            return redirect('/')

        except Exception as e:
            messages.error(request, f'회원가입 중 오류가 발생했습니다: {str(e)}')
            return render(request, self.template_name)


class LogoutView(View):
    """
    Logout
    """
    def get(self, request):
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
        return redirect('/')

    def post(self, request):
        logout(request)
        messages.success(request, '로그아웃되었습니다.')
        return redirect('/')
