"""
Custom User model
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.common.models import TimeStampedModel
from apps.common.validators import validate_image_file


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
