# 공통 백엔드 구현 상세 문서

## 구현 개요

SKILL.md에 명시된 요구사항을 기반으로 Python 3.12, Django 5.1.4를 사용하여 공통 백엔드를 구축했습니다.

## 구현된 주요 기능

### 1. Django 프로젝트 구조

```
1team-project/
├── apps/
│   ├── common/              # 공통 모듈
│   │   ├── models.py        # TimeStampedModel, SoftDeleteModel, BaseModel
│   │   ├── permissions.py   # IsOwner, IsOwnerOrReadOnly, IsCreatorOrAdmin
│   │   ├── exceptions.py    # custom_exception_handler
│   │   └── validators.py    # 파일 검증 함수들
│   └── users/               # 사용자 관리
│       ├── models.py        # Custom User Model
│       ├── serializers.py   # User Serializers
│       ├── views.py         # User API Views
│       ├── urls.py          # User URLs
│       └── admin.py         # User Admin
├── config/
│   ├── settings.py          # Django 설정
│   ├── urls.py              # 루트 URL 설정
│   ├── celery.py            # Celery 설정
│   ├── wsgi.py              # WSGI 설정
│   └── asgi.py              # ASGI 설정
├── docker-compose.yml       # Docker Compose 설정
├── Dockerfile               # Docker 이미지
├── manage.py                # Django 관리 도구
└── requirements-*.txt       # 의존성 관리
```

### 2. Custom User Model (apps/users/models.py)

**주요 특징:**
- `AbstractUser`를 상속하여 Django의 기본 User 확장
- **이메일을 username 필드로 사용** (username 필드 제거)
- 추가 필드:
  - `nickname`: 닉네임 (unique)
  - `avatar`: 프로필 이미지
  - `bio`: 자기소개
  - `role`: 사용자 역할 (user/creator/admin)
  - `is_email_verified`: 이메일 인증 여부
  - `phone_number`: 전화번호
  - `birth_date`: 생년월일

**UserManager:**
- `create_user()`: 일반 사용자 생성
- `create_superuser()`: 관리자 생성

### 3. JWT 인증 시스템

**설정 (config/settings.py):**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=1440),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}
```

**주요 기능:**
- Access Token: 60분 유효
- Refresh Token: 24시간 유효
- 토큰 갱신 시 새 토큰 발급 (Rotation)
- 로그아웃 시 토큰 블랙리스트 처리

### 4. API 엔드포인트

#### 인증 관련
- `POST /api/v1/auth/register/` - 회원가입
- `POST /api/v1/auth/login/` - 로그인
- `POST /api/v1/auth/logout/` - 로그아웃
- `POST /api/v1/auth/refresh/` - 토큰 갱신

#### 사용자 프로필
- `GET /api/v1/auth/me/` - 프로필 조회
- `PUT /api/v1/auth/me/` - 프로필 전체 수정
- `PATCH /api/v1/auth/me/` - 프로필 부분 수정
- `PATCH /api/v1/auth/me/avatar/` - 프로필 이미지 업로드
- `POST /api/v1/auth/me/password/` - 비밀번호 변경
- `DELETE /api/v1/auth/me/delete/` - 계정 삭제

#### 기타
- `GET /api/v1/health/` - 헬스 체크
- `GET /api/docs/` - Swagger API 문서
- `GET /api/redoc/` - ReDoc API 문서

### 5. 공통 Base Models (apps/common/models.py)

#### TimeStampedModel
```python
- created_at: 생성일시 (자동)
- updated_at: 수정일시 (자동)
```

#### SoftDeleteModel
```python
- is_active: 활성화 여부
- deleted_at: 삭제일시
- soft_delete(): Soft delete 메서드
- restore(): 복구 메서드
```

#### BaseModel
- TimeStampedModel + SoftDeleteModel 결합

### 6. 권한 시스템 (apps/common/permissions.py)

#### IsOwner
- 객체의 소유자만 접근 가능
- `obj.user`, `obj.owner` 또는 객체 자체가 사용자인 경우 체크

#### IsOwnerOrReadOnly
- 읽기는 모든 사용자 가능
- 쓰기는 소유자만 가능

#### IsCreatorOrAdmin
- 크리에이터 또는 관리자만 접근 가능

### 7. 파일 업로드 검증 (apps/common/validators.py)

#### validate_file_size
- 파일 크기 검증 (기본 100MB)

#### validate_image_file
- 이미지 파일 타입 검증
- 허용: JPEG, PNG, GIF, WebP
- `python-magic`을 사용한 MIME 타입 검증

#### validate_audio_file
- 오디오 파일 타입 검증
- 허용: MP3, WAV, OGG, MP4

#### validate_video_file
- 비디오 파일 타입 검증
- 허용: MP4, WebM, OGG

### 8. 에러 핸들링 (apps/common/exceptions.py)

**custom_exception_handler:**
- DRF의 기본 예외 핸들러 확장
- 일관된 에러 응답 형식:
```json
{
  "error": true,
  "message": "에러 메시지",
  "details": {},
  "status_code": 400
}
```
- 모든 에러 자동 로깅

### 9. REST Framework 설정

**인증:**
- JWT 인증 (JWTAuthentication)

**권한:**
- 기본적으로 인증 필요 (IsAuthenticated)

**Pagination:**
- PageNumberPagination (20개/페이지)

**Filtering:**
- DjangoFilterBackend
- SearchFilter
- OrderingFilter

**Throttling:**
- 익명 사용자: 100/시간
- 인증 사용자: 1000/시간

### 10. Celery 설정

**config/celery.py:**
- Redis를 메시지 브로커로 사용
- 자동 태스크 탐색 (autodiscover_tasks)
- 비동기 작업 처리 준비

**사용 예시:**
```python
@app.task
def process_media_file(file_id):
    # 미디어 파일 처리
    pass
```

### 11. Docker 설정

**docker-compose.yml 서비스:**
- `db`: PostgreSQL 16
- `redis`: Redis 7
- `web`: Django 애플리케이션
- `celery_worker`: Celery Worker
- `celery_beat`: Celery Beat Scheduler

**환경:**
- Python 3.12-slim 이미지 사용
- Gunicorn WSGI 서버 (4 workers)
- PostgreSQL과 Redis 헬스 체크

### 12. API 문서화

**drf-spectacular:**
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`
- 모든 API 자동 문서화

### 13. 보안 설정

**개발 환경:**
- DEBUG=True
- 로컬 CORS 허용

**프로덕션 환경 (DEBUG=False 시):**
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `X_FRAME_OPTIONS = 'DENY'`

### 14. 로깅 설정

**로그 레벨:**
- INFO 이상 로그 기록
- 개발: 콘솔 출력
- 프로덕션: 콘솔 + 파일 출력

**로그 파일:**
- `logs/django.log`

## 데이터베이스 설계

### User 테이블 (users)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | BigAutoField | Primary Key |
| email | EmailField | 이메일 (Unique, Username) |
| password | CharField | 암호화된 비밀번호 |
| nickname | CharField | 닉네임 (Unique) |
| avatar | ImageField | 프로필 이미지 |
| bio | TextField | 자기소개 |
| role | CharField | 역할 (user/creator/admin) |
| is_email_verified | BooleanField | 이메일 인증 여부 |
| phone_number | CharField | 전화번호 |
| birth_date | DateField | 생년월일 |
| is_active | BooleanField | 활성화 여부 |
| is_staff | BooleanField | 스태프 여부 |
| is_superuser | BooleanField | 슈퍼유저 여부 |
| last_login | DateTimeField | 마지막 로그인 |
| created_at | DateTimeField | 생성일시 |
| updated_at | DateTimeField | 수정일시 |

## 의존성 관리

### requirements-base.txt
- Django 5.1.4
- djangorestframework 3.15.2
- djangorestframework-simplejwt 5.4.0
- psycopg2-binary 2.9.10 (PostgreSQL)
- django-cors-headers 4.6.0
- Pillow 11.0.0 (이미지 처리)
- python-magic 0.4.27 (파일 타입 검증)
- celery 5.4.0
- redis 5.2.1
- python-decouple 3.8
- cryptography 44.0.0
- drf-spectacular 0.28.0
- django-health-check 3.18.3

### requirements-dev.txt
- pytest 8.3.4
- pytest-django 4.9.0
- pytest-cov 6.0.0
- black 24.10.0
- isort 5.13.2
- flake8 7.1.1
- pylint 3.3.3
- django-debug-toolbar 4.4.6
- ipython 8.31.0

### requirements-prod.txt
- gunicorn 23.0.0
- sentry-sdk 2.19.2
- django-anymail 13.0

## 개발 가이드

### 새로운 앱 추가하기

1. 앱 생성:
```bash
python manage.py startapp app_name apps/app_name
```

2. `apps/app_name/apps.py` 수정:
```python
class AppNameConfig(AppConfig):
    name = 'apps.app_name'
```

3. `config/settings.py`의 INSTALLED_APPS에 추가:
```python
INSTALLED_APPS = [
    ...
    'apps.app_name',
]
```

4. 모델에서 공통 Base 모델 사용:
```python
from apps.common.models import BaseModel

class MyModel(BaseModel):
    # 자동으로 created_at, updated_at, is_active, deleted_at 포함
    title = models.CharField(max_length=200)
```

### API View 작성 예시

```python
from rest_framework import generics
from apps.common.permissions import IsOwner

class MyAPIView(generics.ListCreateAPIView):
    permission_classes = [IsOwner]
    serializer_class = MySerializer

    def get_queryset(self):
        return MyModel.objects.filter(user=self.request.user)
```

### 파일 업로드 모델 예시

```python
from apps.common.validators import validate_audio_file

class AudioFile(BaseModel):
    file = models.FileField(
        upload_to='audio/%Y/%m/%d/',
        validators=[validate_audio_file]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
```

## 테스트 가이드

### 단위 테스트 작성

```python
# apps/users/tests/test_models.py
from django.test import TestCase
from apps.users.models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            nickname='testuser',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
```

### API 테스트 작성

```python
# apps/users/tests/test_api.py
from rest_framework.test import APITestCase
from apps.users.models import User

class UserAPITest(APITestCase):
    def test_register(self):
        data = {
            'email': 'test@example.com',
            'nickname': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/register/', data)
        self.assertEqual(response.status_code, 201)
```

## 배포 가이드

### Docker로 프로덕션 배포

1. 환경변수 설정:
```bash
cp .env.example .env
# .env 파일에서 SECRET_KEY, DB 정보 등 수정
```

2. Docker Compose로 실행:
```bash
docker-compose up -d --build
```

3. 마이그레이션:
```bash
docker-compose exec web python manage.py migrate
```

4. 정적 파일 수집:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

5. 슈퍼유저 생성:
```bash
docker-compose exec web python manage.py createsuperuser
```

## 다음 개발 단계

### Phase 2 추가 기능
1. **이메일 인증**
   - 회원가입 시 이메일 인증 메일 발송
   - 인증 토큰 검증

2. **비밀번호 재설정**
   - 비밀번호 재설정 메일 발송
   - 재설정 토큰 검증

3. **소셜 로그인**
   - Google OAuth
   - GitHub OAuth

4. **AWS S3 연동**
   - 미디어 파일을 S3에 저장
   - CDN 연동

5. **서비스별 앱 개발**
   - Music 앱: 음악 업로드, 플레이리스트
   - Podcast 앱: 에피소드, 채널 관리
   - Video 앱: 비디오 업로드, 인코딩

## 참고사항

- Python 버전: 3.12
- Django 버전: 5.1.4
- 데이터베이스: PostgreSQL 16
- 캐시/메시지 브로커: Redis 7
- 모든 비밀번호는 Django의 기본 해시 알고리즘으로 암호화
- API 요청 시 `Authorization: Bearer <access_token>` 헤더 필요
- 파일 업로드는 multipart/form-data 형식 사용

## 문제 해결

### 일반적인 문제

1. **Migration 오류**
```bash
# 모든 마이그레이션 삭제 후 재생성
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

2. **Static 파일 404**
```bash
python manage.py collectstatic --noinput
```

3. **Celery 연결 오류**
```bash
# Redis 실행 확인
redis-cli ping
```

이 문서는 공통 백엔드의 구현 세부사항을 설명합니다. 추가 질문이나 개선사항은 이슈를 등록해주세요.
