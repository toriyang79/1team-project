"""
Common API views for authentication
"""

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.users.serializers import UserSerializer, UserRegistrationSerializer
from .serializers import LoginSerializer


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
