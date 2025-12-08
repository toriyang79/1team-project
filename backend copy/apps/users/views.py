"""
User views
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    AvatarUploadSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="회원가입",
        description="새로운 사용자 계정을 생성합니다.",
        responses={
            201: OpenApiResponse(description="회원가입 성공"),
            400: OpenApiResponse(description="잘못된 요청")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': '회원가입이 완료되었습니다.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer

    @extend_schema(
        summary="내 프로필 조회",
        description="현재 로그인한 사용자의 프로필을 조회합니다.",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="프로필 수정",
        description="현재 로그인한 사용자의 프로필을 수정합니다.",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="프로필 부분 수정",
        description="현재 로그인한 사용자의 프로필을 부분적으로 수정합니다.",
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="비밀번호 변경",
        description="현재 로그인한 사용자의 비밀번호를 변경합니다.",
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description="비밀번호 변경 성공"),
            400: OpenApiResponse(description="잘못된 요청")
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'message': '비밀번호가 성공적으로 변경되었습니다.'
        }, status=status.HTTP_200_OK)


class AvatarUploadView(generics.UpdateAPIView):
    """
    Upload or update user avatar
    """
    serializer_class = AvatarUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="프로필 이미지 업로드",
        description="프로필 이미지를 업로드하거나 변경합니다.",
        request=AvatarUploadSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': '프로필 이미지가 업데이트되었습니다.'
        }, status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    """
    Delete user account
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="계정 삭제",
        description="현재 로그인한 사용자의 계정을 삭제합니다.",
        responses={
            204: OpenApiResponse(description="계정 삭제 성공"),
        }
    )
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()

        return Response({
            'message': '계정이 삭제되었습니다.'
        }, status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    """
    Logout user by blacklisting refresh token
    """
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
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                'message': '로그아웃되었습니다.'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'error': '잘못된 토큰입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)


# API Key Management Views

class APIKeyListCreateView(generics.ListCreateAPIView):
    """
    List all API keys or create a new one
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            from .serializers import APIKeyCreateSerializer
            return APIKeyCreateSerializer
        from .serializers import APIKeySerializer
        return APIKeySerializer

    def get_queryset(self):
        from .models import APIKey
        return APIKey.objects.filter(user=self.request.user)

    @extend_schema(
        summary="API Key 목록 조회",
        description="사용자의 모든 API Key를 조회합니다.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="API Key 생성",
        description="새로운 API Key (Public Token)를 생성합니다.",
    )
    def post(self, request, *args, **kwargs):
        from .serializers import APIKeySerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = serializer.save(user=request.user)

        # Return full key only once (on creation)
        response_serializer = APIKeySerializer(api_key)
        return Response({
            'api_key': response_serializer.data,
            'message': 'API Key가 생성되었습니다. 이 키는 다시 확인할 수 없으니 안전한 곳에 보관하세요.'
        }, status=status.HTTP_201_CREATED)


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an API key
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import APIKeySerializer
        return APIKeySerializer

    def get_queryset(self):
        from .models import APIKey
        return APIKey.objects.filter(user=self.request.user)

    @extend_schema(
        summary="API Key 조회",
        description="특정 API Key의 정보를 조회합니다 (key 값은 마스킹됨).",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="API Key 수정",
        description="API Key의 설정을 수정합니다.",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="API Key 삭제",
        description="API Key를 삭제합니다.",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
