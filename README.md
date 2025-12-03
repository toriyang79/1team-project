# Media Platform - 공통 백엔드

풀스택 미디어 플랫폼(Music, Podcast, Video 서비스)의 공통 백엔드 시스템입니다.

## 프로젝트 개요

이 프로젝트는 Music, Podcast, Video 세 가지 미디어 서비스를 위한 공통 백엔드 인프라를 제공합니다. 사용자 인증, 계정 관리, 파일 업로드 등 모든 서비스에서 공통으로 사용하는 핵심 기능을 제공합니다.

## 기술 스택

### Backend
- **Language**: Python 3.12
- **Framework**: Django 5.1.4
- **API**: Django REST Framework 3.15.2
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL 16
- **Cache/Message Broker**: Redis 7
- **Task Queue**: Celery 5.4.0
- **WSGI Server**: Gunicorn 23.0.0

### 주요 라이브러리
- `django-cors-headers`: CORS 설정
- `drf-spectacular`: API 문서화 (Swagger/Redoc)
- `Pillow`: 이미지 처리
- `python-magic`: 파일 타입 검증
- `django-health-check`: 헬스 체크
- `cryptography`: 보안 암호화

## 주요 기능

### 1. 사용자 인증 및 관리
- ✅ JWT 기반 인증 시스템 (Access Token + Refresh Token)
- ✅ 이메일 기반 회원가입/로그인
- ✅ 사용자 프로필 관리 (CRUD)
- ✅ 비밀번호 변경
- ✅ 프로필 이미지 업로드
- ✅ 계정 삭제 (Soft Delete)
- ✅ 사용자 역할 관리 (일반/크리에이터/관리자)

### 2. API 인프라
- ✅ RESTful API 설계
- ✅ API Versioning (`/api/v1/`)
- ✅ CORS 설정
- ✅ Rate Limiting (Throttling)
- ✅ Pagination
- ✅ Filtering & Search
- ✅ 표준화된 에러 핸들링

### 3. 파일 처리
- ✅ 파일 업로드 검증 (크기, 타입, 보안)
- ✅ 이미지/오디오/비디오 파일 타입 검증
- ✅ 파일 크기 제한 (기본 100MB)
- ✅ MIME 타입 검증

### 4. 보안
- ✅ SECRET_KEY 환경변수 관리
- ✅ 비밀번호 암호화
- ✅ SQL Injection 방지
- ✅ XSS/CSRF 보호
- ✅ 파일 업로드 보안 검증

### 5. 공통 모델
- ✅ TimeStampedModel (created_at, updated_at)
- ✅ SoftDeleteModel (is_active, deleted_at)
- ✅ BaseModel (타임스탬프 + Soft Delete)

### 6. 권한 관리
- ✅ IsOwner: 소유자만 접근
- ✅ IsOwnerOrReadOnly: 읽기는 모두, 쓰기는 소유자만
- ✅ IsCreatorOrAdmin: 크리에이터/관리자만 접근

## 프로젝트 구조

```
1team-project/
├── apps/                          # Django 앱들
│   ├── common/                    # 공통 모듈
│   │   ├── models.py             # 공통 Base 모델
│   │   ├── permissions.py        # 권한 클래스
│   │   ├── exceptions.py         # 커스텀 예외 핸들러
│   │   └── validators.py         # 파일 검증 함수
│   └── users/                     # 사용자 앱
│       ├── models.py             # Custom User 모델
│       ├── serializers.py        # 사용자 Serializer
│       ├── views.py              # 사용자 View
│       ├── urls.py               # 사용자 URL
│       └── admin.py              # 사용자 Admin
├── config/                        # 프로젝트 설정
│   ├── settings.py               # Django 설정
│   ├── urls.py                   # 루트 URL
│   ├── wsgi.py                   # WSGI 설정
│   ├── asgi.py                   # ASGI 설정
│   └── celery.py                 # Celery 설정
├── media/                         # 업로드된 미디어 파일
├── staticfiles/                   # 정적 파일
├── logs/                          # 로그 파일
├── .env.example                   # 환경변수 예시
├── .gitignore                     # Git ignore 설정
├── .dockerignore                  # Docker ignore 설정
├── docker-compose.yml             # Docker Compose 설정
├── Dockerfile                     # Docker 이미지 정의
├── manage.py                      # Django 관리 명령어
├── requirements-base.txt          # 기본 의존성
├── requirements-dev.txt           # 개발 의존성
├── requirements-prod.txt          # 프로덕션 의존성
└── README.md                      # 프로젝트 문서
```

## 설치 및 실행 방법

### 사전 요구사항
- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (선택사항)

### 방법 1: Docker를 사용한 실행 (권장)

Docker Compose를 사용하면 Django, PostgreSQL, Redis, Nginx, Celery를 한 번에 실행할 수 있습니다.

#### 1.1 저장소 클론
```bash
git clone <repository-url>
cd 1team-project
```

#### 1.2 환경변수 설정
```bash
# Docker 전용 환경변수 파일 복사
cp .env.docker .env

# .env 파일을 열어 필요한 값들을 수정하세요
# 특히 SECRET_KEY와 DB_PASSWORD는 반드시 변경하세요!
nano .env  # 또는 vim, vi 등 사용
```

**중요 설정 항목:**
- `SECRET_KEY`: Django 시크릿 키 (보안을 위해 반드시 변경)
- `DEBUG`: 프로덕션에서는 `False`로 설정
- `ALLOWED_HOSTS`: 실제 도메인 또는 IP 주소 추가
- `DB_PASSWORD`: PostgreSQL 비밀번호 (강력한 비밀번호로 변경)
- `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`: 자동 관리자 계정 생성 (선택사항)

#### 1.3 Docker Compose로 전체 스택 실행
```bash
# 모든 서비스 빌드 및 백그라운드 실행
docker-compose up -d --build

# 실행 상태 확인
docker-compose ps

# 로그 확인 (실시간)
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f web
docker-compose logs -f nginx
```

**실행되는 서비스:**
- `db`: PostgreSQL 16 데이터베이스
- `redis`: Redis 7 캐시 서버
- `web`: Django 애플리케이션 (Gunicorn)
- `nginx`: Nginx 리버스 프록시
- `celery_worker`: Celery 워커 (비동기 작업)
- `celery_beat`: Celery Beat (스케줄러)

#### 1.4 서비스 접속
- **대시보드**: http://localhost (Nginx를 통해 접속)
- **API**: http://localhost/api/v1/
- **API 문서 (Swagger)**: http://localhost/api/docs/
- **API 문서 (Redoc)**: http://localhost/api/redoc/
- **Admin**: http://localhost/admin/

**포트 정보:**
- Nginx: 80 (HTTP), 443 (HTTPS - SSL 설정 시)
- Django (직접 접속): 8000 (내부 포트, 외부 노출 안 됨)
- PostgreSQL: 5432
- Redis: 6379

#### 1.5 유용한 Docker 명령어
```bash
# 컨테이너 접속 (Django 쉘)
docker-compose exec web python manage.py shell

# 데이터베이스 마이그레이션
docker-compose exec web python manage.py migrate

# 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# 슈퍼유저 생성 (수동)
docker-compose exec web python manage.py createsuperuser

# 컨테이너 내부 Bash 접속
docker-compose exec web bash

# 서비스 재시작
docker-compose restart web

# 특정 서비스만 재빌드
docker-compose up -d --build web

# 모든 서비스 중지
docker-compose stop

# 서비스 중지 및 컨테이너 삭제
docker-compose down

# 볼륨까지 완전 삭제 (데이터베이스 데이터 포함)
docker-compose down -v

# 사용하지 않는 이미지 정리
docker system prune -a
```

#### 1.6 프로덕션 배포 시 추가 설정

**SSL/HTTPS 설정 (Let's Encrypt):**
```bash
# Certbot 컨테이너를 사용한 SSL 인증서 발급
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/certbot:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d your-domain.com \
  -d www.your-domain.com
```

**보안 설정 체크리스트:**
- [ ] `DEBUG=False` 설정
- [ ] `SECRET_KEY` 강력한 값으로 변경
- [ ] `ALLOWED_HOSTS`에 실제 도메인 추가
- [ ] 데이터베이스 비밀번호 변경
- [ ] SSL/HTTPS 설정
- [ ] 방화벽 설정 (필요한 포트만 개방)
- [ ] 정기적인 백업 설정

### 방법 1-2: AWS EC2에 Docker로 배포 (프로덕션)

EC2 인스턴스에 Docker Compose로 전체 스택을 배포합니다. 자세한 내용은 **[EC2 배포 가이드](deploy/EC2_DEPLOYMENT.md)**를 참고하세요.

#### 빠른 시작 (요약)

1. **EC2 인스턴스 생성**
   - Ubuntu 22.04 LTS
   - 최소 t3.small (권장: t3.medium)
   - 보안 그룹: SSH(22), HTTP(80), HTTPS(443)

2. **서버 초기 설정**
   ```bash
   # EC2 접속
   ssh -i "your-key.pem" ubuntu@your-ec2-ip

   # 자동 설정 스크립트 실행 (Docker, UFW, fail2ban 설치)
   sudo bash deploy/ec2-setup.sh
   ```

3. **프로젝트 배포**
   ```bash
   # Git Clone
   cd /home/ubuntu/app
   git clone <repository-url> .

   # 환경변수 설정
   cp .env.docker .env
   vim .env  # SECRET_KEY, DB_PASSWORD 등 수정

   # Docker Compose 실행
   docker compose up -d --build
   ```

4. **SSL 설정 (Let's Encrypt)**
   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

**배포 스크립트:**
- `deploy/ec2-setup.sh`: EC2 서버 초기 설정 (Docker 설치 등)
- `deploy/deploy.sh`: 자동 배포 스크립트 (백업, git pull, 재시작)

**자세한 가이드:** [deploy/EC2_DEPLOYMENT.md](deploy/EC2_DEPLOYMENT.md)

### 방법 2: 로컬 환경에서 실행

1. **저장소 클론**
```bash
git clone <repository-url>
cd 1team-project
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **의존성 설치**
```bash
# 개발 환경
pip install -r requirements-dev.txt

# 프로덕션 환경
pip install -r requirements-prod.txt
```

4. **PostgreSQL 데이터베이스 생성**
```bash
# PostgreSQL에 접속하여 데이터베이스 생성
createdb media_platform
```

5. **환경변수 설정**
```bash
cp .env.example .env
# .env 파일을 열어 DB 설정 등을 수정하세요
```

6. **마이그레이션 실행**
```bash
python manage.py migrate
```

7. **슈퍼유저 생성**
```bash
python manage.py createsuperuser
```

8. **개발 서버 실행**
```bash
python manage.py runserver
```

9. **Celery 실행 (별도 터미널)**
```bash
# Worker
celery -A config worker -l info

# Beat (스케줄러)
celery -A config beat -l info
```

## 웹 대시보드

프로젝트 루트(`http://localhost:8000/`)에 접속하면 관리자 대시보드를 확인할 수 있습니다.

### 주요 기능
- **다크 모드/라이트 모드 전환**: 우측 상단 테마 토글 버튼으로 테마 변경 가능
- **시스템 통계**: 전체 사용자 수, API Key 수 등 실시간 통계 확인
- **API 엔드포인트 목록**: 사용 가능한 모든 API 엔드포인트 한눈에 확인
- **빠른 링크**: API 문서, 관리자 페이지로 바로 이동
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모든 환경 지원

테마 설정은 브라우저 로컬 스토리지에 저장되어 다음 방문 시에도 유지됩니다.

## API 엔드포인트

### 인증 (Authentication)
```
POST   /api/v1/auth/register/          # 회원가입
POST   /api/v1/auth/login/             # 로그인
POST   /api/v1/auth/logout/            # 로그아웃
POST   /api/v1/auth/refresh/           # 토큰 갱신
```

### 사용자 관리 (User Management)
```
GET    /api/v1/auth/me/                # 내 프로필 조회
PUT    /api/v1/auth/me/                # 프로필 수정
PATCH  /api/v1/auth/me/                # 프로필 부분 수정
PATCH  /api/v1/auth/me/avatar/         # 프로필 이미지 변경
POST   /api/v1/auth/me/password/       # 비밀번호 변경
DELETE /api/v1/auth/me/delete/         # 계정 삭제
```

### API Key 관리 (Public Token)
```
GET    /api/v1/auth/api-keys/          # API Key 목록 조회
POST   /api/v1/auth/api-keys/          # API Key 생성
GET    /api/v1/auth/api-keys/{id}/     # API Key 상세 조회
PATCH  /api/v1/auth/api-keys/{id}/     # API Key 수정
DELETE /api/v1/auth/api-keys/{id}/     # API Key 삭제
```

### 헬스 체크
```
GET    /api/v1/health/                 # 서버 상태 확인
```

### API 문서
```
GET    /api/docs/                      # Swagger UI
GET    /api/redoc/                     # ReDoc
GET    /api/schema/                    # OpenAPI Schema
```

## 테스트

```bash
# 전체 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=apps

# 특정 앱 테스트
pytest apps/users/tests/
```

## 개발 도구

### 코드 포맷팅
```bash
# Black (코드 포맷터)
black .

# isort (import 정렬)
isort .
```

### 코드 품질 검사
```bash
# Flake8
flake8 .

# Pylint
pylint apps/
```

## 환경변수 설명

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SECRET_KEY` | Django 시크릿 키 | - |
| `DEBUG` | 디버그 모드 | True |
| `ALLOWED_HOSTS` | 허용된 호스트 | localhost,127.0.0.1 |
| `DB_ENGINE` | 데이터베이스 엔진 | django.db.backends.postgresql |
| `DB_NAME` | 데이터베이스 이름 | media_platform |
| `DB_USER` | 데이터베이스 사용자 | postgres |
| `DB_PASSWORD` | 데이터베이스 비밀번호 | postgres |
| `DB_HOST` | 데이터베이스 호스트 | localhost |
| `DB_PORT` | 데이터베이스 포트 | 5432 |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access Token 유효기간(분) | 60 |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh Token 유효기간(분) | 1440 |
| `MAX_UPLOAD_SIZE` | 최대 업로드 크기(바이트) | 104857600 (100MB) |
| `REDIS_URL` | Redis URL | redis://localhost:6379/0 |

## 구현 세부사항

### Custom User Model
- `AbstractUser`를 상속하여 커스텀 User 모델 구현
- 이메일을 username 필드로 사용
- 닉네임, 프로필 이미지, 소개, 역할 등 추가 필드
- 사용자 역할: 일반 사용자, 크리에이터, 관리자

### JWT 인증
- Access Token: 60분 (기본값)
- Refresh Token: 24시간 (기본값)
- Token Rotation: 리프레시 시 새로운 토큰 발급
- Blacklist: 로그아웃 시 토큰 블랙리스트 처리

### 파일 업로드
- 파일 크기 검증 (최대 100MB)
- MIME 타입 검증 (`python-magic` 사용)
- 허용된 파일 타입:
  - 이미지: JPEG, PNG, GIF, WebP
  - 오디오: MP3, WAV, OGG, MP4
  - 비디오: MP4, WebM, OGG

### 에러 핸들링
- 커스텀 예외 핸들러로 일관된 에러 응답 형식 제공
- 모든 에러 로깅
- 에러 응답 형식:
```json
{
  "error": true,
  "message": "에러 메시지",
  "details": {},
  "status_code": 400
}
```

### 권한 시스템
- `IsOwner`: 객체의 소유자만 접근 가능
- `IsOwnerOrReadOnly`: 읽기는 모두, 쓰기는 소유자만
- `IsCreatorOrAdmin`: 크리에이터와 관리자만 접근

### Celery 태스크 큐
- 비동기 작업 처리 (파일 처리, 이메일 발송 등)
- Redis를 메시지 브로커로 사용
- Celery Beat으로 주기적 작업 스케줄링

### API 문서화
- drf-spectacular를 사용한 자동 API 문서 생성
- Swagger UI와 ReDoc 제공
- OpenAPI 3.0 스펙 준수

## 보안 고려사항

1. **환경변수 관리**: 민감한 정보는 `.env` 파일로 관리
2. **비밀번호 검증**: Django의 기본 비밀번호 검증 사용 (최소 8자)
3. **CORS 설정**: 허용된 Origin만 접근 가능
4. **Rate Limiting**: API 요청 제한 (익명: 100/시간, 인증: 1000/시간)
5. **파일 업로드 보안**: MIME 타입 검증, 파일 크기 제한
6. **HTTPS**: 프로덕션에서 HTTPS 강제 (SSL Redirect)
7. **CSRF 보호**: Django의 기본 CSRF 보호 활성화

## 다음 단계

### Phase 2 개발 계획
- [ ] 이메일 인증 기능
- [ ] 비밀번호 재설정 기능
- [ ] 소셜 로그인 (Google, GitHub)
- [ ] AWS S3 연동
- [ ] 더 많은 테스트 코드 작성
- [ ] CI/CD 파이프라인 구축

### 서비스별 확장
- Music 서비스 앱 개발
- Podcast 서비스 앱 개발
- Video 서비스 앱 개발
- 통합 프론트엔드 개발

## 기여하기

1. 이 저장소를 Fork합니다
2. Feature 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'feat: Add amazing feature'`)
4. 브랜치에 Push합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

### Commit Convention
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 코드
chore: 빌드/설정 변경
```

## 라이센스

This project is licensed under the MIT License.

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**개발 팀**: Media Platform Team
**개발 시작일**: 2025
**Python 버전**: 3.12
**Django 버전**: 5.1.4

## API Key (Public Token) 사용하기

### API Key 생성

1. **JWT 토큰으로 로그인**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "your_password"}'
```

2. **API Key 생성**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/api-keys/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Service API Key",
    "can_read": true,
    "can_write": true,
    "rate_limit": 1000
  }'
```

**응답**:
```json
{
  "api_key": {
    "id": 1,
    "name": "My Service API Key",
    "key": "vF3kL9mP2xQ4wR8tY1nZ5cB7jH6dS0aE...",  // 이 키를 저장하세요!
    "prefix": "vF3kL9mP",
    "is_active": true,
    "can_read": true,
    "can_write": true,
    "rate_limit": 1000,
    "created_at": "2025-01-01T00:00:00Z"
  },
  "message": "API Key가 생성되었습니다. 이 키는 다시 확인할 수 없으니 안전한 곳에 보관하세요."
}
```

### API Key로 인증하기

생성된 API Key를 `X-API-Key` 헤더에 넣어서 사용:

```bash
curl -X GET http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "X-API-Key: vF3kL9mP2xQ4wR8tY1nZ5cB7jH6dS0aE..."
```

### API Key 관리

```bash
# API Key 목록 조회
GET /api/v1/auth/api-keys/

# 특정 API Key 조회
GET /api/v1/auth/api-keys/{id}/

# API Key 수정 (활성화/비활성화, 권한 변경)
PATCH /api/v1/auth/api-keys/{id}/

# API Key 삭제
DELETE /api/v1/auth/api-keys/{id}/
```

### API Key 권한

- **can_read**: 읽기 권한 (GET 요청)
- **can_write**: 쓰기 권한 (POST, PUT, PATCH 요청)
- **can_delete**: 삭제 권한 (DELETE 요청)
- **rate_limit**: 시간당 요청 제한 (기본 1000)

### 사용 예시

#### Python
```python
import requests

API_KEY = "vF3kL9mP2xQ4wR8tY1nZ5cB7jH6dS0aE..."
headers = {"X-API-Key": API_KEY}

# API 호출
response = requests.get(
    "http://127.0.0.1:8000/api/v1/auth/me/",
    headers=headers
)
print(response.json())
```

#### JavaScript
```javascript
const API_KEY = "vF3kL9mP2xQ4wR8tY1nZ5cB7jH6dS0aE...";

fetch("http://127.0.0.1:8000/api/v1/auth/me/", {
  headers: {
    "X-API-Key": API_KEY
  }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

### JWT vs API Key 비교

| 항목 | JWT Token | API Key (Public Token) |
|------|-----------|----------------------|
| 유효기간 | 60분 (갱신 가능) | 무제한 (만료일 설정 가능) |
| 용도 | 사용자 인증 | 서비스/앱 인증 |
| 헤더 | `Authorization: Bearer <token>` | `X-API-Key: <key>` |
| 권한 관리 | 사용자 역할 기반 | API Key별 권한 설정 |
| Rate Limiting | 1000/시간 | 커스터마이징 가능 |

