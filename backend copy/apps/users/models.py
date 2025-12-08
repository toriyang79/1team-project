"""
Custom User model
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from apps.common.models import TimeStampedModel
from apps.common.validators import validate_image_file
import secrets


class UserManager(BaseUserManager):
    """
    Custom user manager
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('이메일은 필수입니다.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    """
    Custom User model with email as username field
    """
    ROLE_CHOICES = [
        ('user', '일반 사용자'),
        ('creator', '크리에이터'),
        ('admin', '관리자'),
    ]

    username = None  # Remove username field
    email = models.EmailField(unique=True, verbose_name='이메일')
    nickname = models.CharField(max_length=50, unique=True, verbose_name='닉네임')
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[validate_image_file],
        verbose_name='프로필 이미지'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='소개')
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='역할'
    )
    is_email_verified = models.BooleanField(default=False, verbose_name='이메일 인증 여부')
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='전화번호'
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name='생년월일')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def is_creator(self):
        """Check if user is a creator"""
        return self.role in ['creator', 'admin']


class APIKey(TimeStampedModel):
    """
    API Key model for service authentication (Public Token)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys', verbose_name='사용자')
    name = models.CharField(max_length=100, verbose_name='API Key 이름')
    key = models.CharField(max_length=64, unique=True, verbose_name='API Key')
    prefix = models.CharField(max_length=8, verbose_name='Key Prefix')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='마지막 사용일시')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='만료일시')

    # Permissions
    can_read = models.BooleanField(default=True, verbose_name='읽기 권한')
    can_write = models.BooleanField(default=False, verbose_name='쓰기 권한')
    can_delete = models.BooleanField(default=False, verbose_name='삭제 권한')

    # Rate limiting
    rate_limit = models.IntegerField(default=1000, verbose_name='시간당 요청 제한')

    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.prefix}...)"

    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        return secrets.token_urlsafe(48)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.prefix = self.key[:8]
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if API key is valid"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
