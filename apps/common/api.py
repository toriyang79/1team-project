"""
Common API views for authentication
"""

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.shortcuts import redirect
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from apps.users.serializers import UserSerializer, UserRegistrationSerializer
from .serializers import LoginSerializer
import requests


class LoginAPIView(APIView):
    """로그인 API"""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="로그인",
        description="이메일과 비밀번호로 로그인하고 JWT 토큰을 발급받습니다.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="로그인 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': f'{user.nickname}님, 환영합니다!'
        }, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    """회원가입 API"""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="회원가입",
        description="새로운 사용자 계정을 생성하고 JWT 토큰을 발급받습니다.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="회원가입 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': f'{user.nickname}님, 회원가입을 환영합니다!'
        }, status=status.HTTP_201_CREATED)


class LogoutAPIView(APIView):
    """로그아웃 API"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="로그아웃",
        description="리프레시 토큰을 블랙리스트에 추가하여 로그아웃합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh': {'type': 'string'}
                }
            }
        },
        responses={
            200: OpenApiResponse(description="로그아웃 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'error': '리프레시 토큰이 필요합니다.'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                'message': '로그아웃되었습니다.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': '잘못된 토큰입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)


class MeAPIView(APIView):
    """현재 사용자 정보 조회 API"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="내 정보 조회",
        description="현재 로그인한 사용자의 정보를 조회합니다.",
        responses={
            200: UserSerializer,
        }
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialLoginAPIView(APIView):
    """소셜 로그인 리다이렉트 API"""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="소셜 로그인 시작",
        description="지정된 소셜 프로바이더로 로그인을 시작합니다.",
        responses={
            302: OpenApiResponse(description="OAuth 제공자로 리다이렉트"),
        }
    )
    def get(self, request, provider):
        """
        소셜 로그인 시작 엔드포인트
        provider: google, github, naver, kakao
        """
        frontend_url = request.GET.get('redirect_uri', settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000')

        # Django Allauth의 소셜 로그인 URL로 리다이렉트
        # state 파라미터로 프론트엔드 URL 전달
        redirect_url = f'/accounts/{provider}/login/?next=/api/v1/social/callback/{provider}/?frontend={frontend_url}'
        return redirect(redirect_url)


class SocialCallbackAPIView(APIView):
    """소셜 로그인 콜백 처리 API"""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="소셜 로그인 콜백",
        description="OAuth 제공자로부터 콜백을 받아 JWT 토큰을 발급합니다.",
        responses={
            302: OpenApiResponse(description="프론트엔드로 토큰과 함께 리다이렉트"),
        }
    )
    def get(self, request, provider):
        """
        소셜 로그인 콜백 처리
        인증 후 JWT 토큰 발급하고 프론트엔드로 리다이렉트
        """
        if not request.user.is_authenticated:
            frontend_url = request.GET.get('frontend', 'http://localhost:3000')
            return redirect(f'{frontend_url}/login?error=authentication_failed')

        # JWT 토큰 생성
        user = request.user
        refresh = RefreshToken.for_user(user)

        # 프론트엔드로 리다이렉트 (토큰을 URL 파라미터로 전달)
        frontend_url = request.GET.get('frontend', 'http://localhost:3000')
        redirect_url = f'{frontend_url}/social-callback?access_token={str(refresh.access_token)}&refresh_token={str(refresh)}'

        return redirect(redirect_url)
