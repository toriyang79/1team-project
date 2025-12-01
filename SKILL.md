# Team Skills & Tech Stack

## Project Overview
풀스택 미디어 플랫폼 (Music, Podcast, Video 서비스)

## Role Distribution

### A: 공통 백엔드 리드
- 사용자 인증/인가 (JWT)
- 계정 관리 시스템
- 공통 API 인프라
- 데이터베이스 설계 (공통 모델)
- 미디어 파일 처리 공통 로직

### B: Music 서비스 리드
- 인디/연습곡 공유 기능
- 오디오 파일 업로드/스트리밍
- 플레이리스트 관리
- Music 특화 메타데이터 처리

### C: Podcast 서비스 리드
- 짧은 자기계발/수다 콘텐츠
- 팟캐스트 에피소드 관리
- 오디오 스트리밍
- 시리즈/채널 관리

### D: Video 서비스 + 메인 페이지 리드
- 짧은 튜토리얼/하이라이트 클립
- 비디오 인코딩/스트리밍
- 메인 페이지 설계
- 통합 UI/UX

### 공통 (DevOps/Docker/문서)
- 모든 팀원이 협업
- 1명이 방향성 리드

---

## Tech Stack

### Backend (공통)
- **Framework**: Django (버전 고정 필요)
- **Language**: Python (버전 고정 필요)
- **Database**: PostgreSQL (권장) / MySQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API**: Django REST Framework (DRF)
- **Task Queue**: Celery (미디어 처리용)
- **Message Broker**: Redis

### 공통 백엔드 필수 기술

#### 1. Authentication & Authorization
- JWT Token 기반 인증
- Access Token + Refresh Token
- Token 갱신 로직
- 권한 관리 (Permission Classes)
- 소셜 로그인 (선택)

#### 2. User Management
- Django User Model (Custom User)
- 프로필 관리 (CRUD)
- 이메일 인증
- 비밀번호 재설정
- 사용자 역할 (일반/크리에이터/관리자)

#### 3. API Infrastructure
- RESTful API 설계
- API Versioning (`/api/v1/...`)
- CORS 설정 (django-cors-headers)
- Rate Limiting (throttling)
- Pagination
- Filtering & Search

#### 4. Media File Handling
- 파일 업로드 처리
- 파일 검증 (크기, 타입, 보안)
- Storage 추상화 (로컬/S3)
- 썸네일 생성 (Pillow)
- CDN 연동 준비

#### 5. Database Design
- 공통 Base Model (created_at, updated_at, is_active)
- User Model
- 서비스 간 참조 관계 설계
- Migration 관리

#### 6. Error Handling & Logging
- Custom Exception Handler
- 로그 파일 관리
- 에러 응답 표준화
- 디버깅 도구 (Django Debug Toolbar)

#### 7. Testing
- Unit Test (Django TestCase)
- API Test (DRF APITestCase)
- Coverage 목표 설정

#### 8. Security
- SECRET_KEY 관리
- SQL Injection 방지
- XSS 방지
- CSRF 보호
- 파일 업로드 보안

### Frontend (공통)
- **Framework**: React / Vue.js (팀 결정 필요)
- **State Management**: Redux / Vuex
- **HTTP Client**: Axios
- **UI Library**: Material-UI / Tailwind CSS

### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions (권장)
- **Server**: Nginx + Gunicorn
- **Cloud**: AWS / GCP / Azure (선택)
- **Storage**: AWS S3 / MinIO

---

## Development Guidelines

### Git Strategy
- **Main Branch**: `main` (배포용)
- **Feature Branches**: `feature/{service}/{feature-name}`
  - 예: `feature/auth/jwt-login`
  - 예: `feature/music/upload`
- **Bugfix Branches**: `bugfix/{description}`
- **Direct push to main**: ❌ 금지
- **PR Required**: ✅ 필수

### Commit Convention
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅 (기능 변경 없음)
refactor: 코드 리팩토링
test: 테스트 코드
chore: 빌드/설정 변경
```

**Example**:
```
feat: JWT 인증 시스템 구현
fix: 파일 업로드 시 확장자 검증 오류 수정
docs: API 문서 업데이트
```

### Code Review Rules
- 모든 PR은 최소 1명 이상의 리뷰 필요
- 리뷰 승인 후 merge
- Merge 방식: Squash and Merge (권장)

### Version Lock
```
Python: 3.11.x (팀 합의 후 고정)
Django: 5.0.x (팀 합의 후 고정)
djangorestframework: 3.14.x
```

---

## 공통 백엔드 개발 우선순위

### Phase 1: 기본 인프라 (Week 1-2)
1. Django 프로젝트 초기 설정
2. Custom User Model 구현
3. JWT 인증 시스템
4. 기본 API 구조 (CORS, Error Handling)
5. Docker 환경 설정

### Phase 2: 핵심 기능 (Week 3-4)
1. 사용자 회원가입/로그인 API
2. 프로필 관리 API
3. 파일 업로드 공통 로직
4. 권한 관리 시스템
5. 데이터베이스 마이그레이션

### Phase 3: 통합 및 최적화 (Week 5+)
1. 다른 서비스와 통합 테스트
2. API 문서화 (Swagger/Redoc)
3. 성능 최적화
4. 보안 강화
5. 배포 준비

---

## Dependencies (공통 백엔드)

```txt
# Core
Django>=5.0,<5.1
djangorestframework>=3.14,<3.15
djangorestframework-simplejwt>=5.3,<6.0

# Database
psycopg2-binary>=2.9  # PostgreSQL
# or mysqlclient>=2.2  # MySQL

# CORS
django-cors-headers>=4.3

# File Upload
Pillow>=10.0  # Image processing
python-magic>=0.4  # File type detection

# Task Queue
celery>=5.3
redis>=5.0

# Environment
python-decouple>=3.8
python-dotenv>=1.0

# Testing
pytest>=7.4
pytest-django>=4.5
coverage>=7.3

# Security
django-ratelimit>=4.1

# Development
django-debug-toolbar>=4.2
ipython>=8.17
```

---

## API Endpoints (공통 백엔드)

### Authentication
```
POST   /api/v1/auth/register/          # 회원가입
POST   /api/v1/auth/login/             # 로그인
POST   /api/v1/auth/logout/            # 로그아웃
POST   /api/v1/auth/refresh/           # 토큰 갱신
POST   /api/v1/auth/password/reset/    # 비밀번호 재설정
```

### User Management
```
GET    /api/v1/users/me/               # 내 프로필 조회
PUT    /api/v1/users/me/               # 프로필 수정
PATCH  /api/v1/users/me/avatar/        # 프로필 이미지 변경
DELETE /api/v1/users/me/               # 계정 삭제
```

### Health Check
```
GET    /api/v1/health/                 # 서버 상태 확인
```

---

## Environment Variables

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=media_platform
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (1 day)

# File Upload
MEDIA_ROOT=/media
MAX_UPLOAD_SIZE=104857600  # 100MB

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (선택)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

---

## Learning Resources

### 공통 백엔드 팀원이 학습할 내용
1. Django REST Framework 공식 문서
2. JWT 인증 원리
3. RESTful API 설계 원칙
4. 데이터베이스 정규화
5. Docker 기본 사용법
6. Git 협업 워크플로우

### Recommended Reading
- Django for APIs (William S. Vincent)
- Two Scoops of Django
- REST API Design Rulebook

---

## Communication

### Daily Standup (권장)
- 어제 한 일
- 오늘 할 일
- 블로커/이슈

### Weekly Sync
- 진행 상황 공유
- 통합 이슈 논의
- 다음 주 계획

### Tools
- Slack / Discord (커뮤니케이션)
- Notion / Confluence (문서)
- Jira / GitHub Issues (태스크 관리)
- Figma (디자인 공유)

---

## Success Criteria

### 공통 백엔드 완성 기준
- [ ] JWT 인증 시스템 완전 작동
- [ ] 회원가입/로그인 API 안정화
- [ ] 파일 업로드 검증 및 저장 로직 완성
- [ ] 모든 API 문서화 완료
- [ ] 단위 테스트 커버리지 70% 이상
- [ ] Docker 환경에서 정상 실행
- [ ] 다른 서비스와 통합 성공

---

## Notes
- 각 서비스는 공통 백엔드의 User 모델을 참조합니다
- 공통 백엔드가 안정화된 후 다른 서비스 개발이 본격화됩니다
- API 변경 시 반드시 다른 팀원에게 공지하세요
- 보안은 타협하지 마세요 (특히 인증/파일 업로드)
