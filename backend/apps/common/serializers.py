"""
Common serializers for authentication
"""

from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """로그인 Serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )

            if not user:
                raise serializers.ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')

            if not user.is_active:
                raise serializers.ValidationError('비활성화된 계정입니다.')

            data['user'] = user
        else:
            raise serializers.ValidationError('이메일과 비밀번호를 입력해주세요.')

        return data
