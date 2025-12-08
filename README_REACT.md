# Artlion - React + Django 풀스택 프로젝트

AI 창작물(이미지, 음악, 비디오)을 공유하고 발견하는 플랫폼입니다.

## 🛠 기술 스택

### Backend
- **Django 4.x** - Python 웹 프레임워크
- **Django REST Framework** - REST API
- **JWT Authentication** - Simple JWT를 사용한 인증
- **PostgreSQL** - 데이터베이스
- **Redis** - 캐싱 및 Celery 브로커
- **Nginx** - 리버스 프록시 및 정적 파일 서빙

### Frontend
- **React 18+** with **TypeScript**
- **React Router v6** - 클라이언트 사이드 라우팅
- **Axios** - HTTP 클라이언트
- **Tailwind CSS** - 유틸리티 우선 CSS 프레임워크
- **Context API** - 전역 상태 관리 (인증)

## 📁 프로젝트 구조

```
1team-project2/
├── apps/                      # Django 앱들
│   ├── common/               # 공통 기능 (로그인, 회원가입)
│   │   ├── api.py           # REST API 뷰
│   │   ├── serializers.py   # API 시리얼라이저
│   │   ├── urls.py          # API URL 라우팅
│   │   └── views.py         # Django 템플릿 뷰
│   └── users/               # 사용자 관리
│       ├── models.py        # User 모델
│       ├── serializers.py   # 사용자 시리얼라이저
│       └── views.py         # 사용자 API 뷰
├── config/                   # Django 설정
│   ├── settings.py          # 메인 설정
│   └── urls.py              # URL 라우팅
├── frontend/                 # React 프론트엔드
│   ├── public/              # 정적 파일
│   ├── src/
│   │   ├── contexts/        # React Context (AuthContext)
│   │   ├── pages/           # 페이지 컴포넌트
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── services/        # API 서비스
│   │   │   ├── api.ts       # Axios 인스턴스
│   │   │   └── authService.ts
│   │   ├── App.tsx          # 메인 앱 컴포넌트
│   │   └── index.tsx        # 엔트리 포인트
│   ├── .env                 # 개발 환경 변수
│   ├── .env.production      # 프로덕션 환경 변수
│   └── package.json
├── templates/               # Django 템플릿 (레거시)
└── docker-compose.yml       # Docker 구성
```

## 🚀 시작하기

### 사전 요구사항

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (선택사항)

### 1. 백엔드 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements-dev.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 추가

# 데이터베이스 마이그레이션
python manage.py migrate

# 슈퍼유저 생성
python manage.py createsuperuser

# 개발 서버 실행
python manage.py runserver
```

백엔드 서버가 http://localhost:8000 에서 실행됩니다.

### 2. 프론트엔드 설정

```bash
# frontend 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

프론트엔드 개발 서버가 http://localhost:3000 에서 실행됩니다.

## 🔐 인증 시스템

### JWT 토큰 기반 인증

1. **로그인**: `/api/v1/login/` - 이메일과 비밀번호로 로그인
2. **회원가입**: `/api/v1/register/` - 새 계정 생성
3. **로그아웃**: `/api/v1/logout/` - 리프레시 토큰 블랙리스트 등록
4. **내 정보**: `/api/v1/me/` - 현재 사용자 정보 조회

### 토큰 저장

- **Access Token**: HTTP Authorization 헤더에 포함 (`Bearer {token}`)
- **Refresh Token**: 로컬 스토리지에 저장
- 토큰 만료 시 자동 갱신 (Axios 인터셉터)

## 📡 API 엔드포인트

### 인증 API
```
POST   /api/v1/login/          # 로그인
POST   /api/v1/register/       # 회원가입
POST   /api/v1/logout/         # 로그아웃
GET    /api/v1/me/             # 내 정보 조회
```

### 사용자 API
```
GET    /api/v1/auth/profile/           # 프로필 조회
PUT    /api/v1/auth/profile/           # 프로필 수정
POST   /api/v1/auth/password/change/   # 비밀번호 변경
PATCH  /api/v1/auth/avatar/            # 프로필 이미지 업로드
DELETE /api/v1/auth/delete/            # 계정 삭제
```

### API 문서
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema: http://localhost:8000/api/schema/

## 🎨 프론트엔드 구조

### Context API - 인증 상태 관리

```typescript
// AuthContext 사용 예시
import { useAuth } from './contexts/AuthContext';

function Component() {
  const { user, isAuthenticated, login, logout } = useAuth();

  // ...
}
```

### API 서비스

```typescript
// authService 사용 예시
import authService from './services/authService';

// 로그인
const response = await authService.login({ email, password });

// 현재 사용자 조회
const user = await authService.getCurrentUser();
```

## 🏗 프로덕션 빌드

### 프론트엔드 빌드

```bash
cd frontend
npm run build
```

빌드된 파일은 `frontend/build/` 디렉토리에 생성됩니다.

### Nginx 설정 예시

```nginx
server {
    listen 80;
    server_name www.artlion.p-e.kr;

    # React 정적 파일
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Django API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Django Static/Media
    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

## 🔧 환경 변수

### Backend (.env)
```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=artlion_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://www.artlion.p-e.kr

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### Frontend (.env)
```env
# API URL
REACT_APP_API_URL=http://localhost:8000/api/v1

# App Settings
REACT_APP_NAME=Artlion
REACT_APP_VERSION=1.0.0
```

## 📝 개발 가이드

### 새로운 API 엔드포인트 추가

1. **Serializer 작성** (`serializers.py`)
2. **View/ViewSet 작성** (`api.py` 또는 `views.py`)
3. **URL 라우팅** (`urls.py`)
4. **프론트엔드 서비스 함수 추가** (`services/`)

### 새로운 React 페이지 추가

1. **컴포넌트 작성** (`src/pages/NewPage.tsx`)
2. **라우팅 추가** (`App.tsx`)
3. **필요시 Context 업데이트**

## 🐛 트러블슈팅

### CORS 에러
- `CORS_ALLOWED_ORIGINS`에 프론트엔드 URL 추가
- `CSRF_TRUSTED_ORIGINS`에도 동일하게 추가

### 401 Unauthorized
- 토큰이 만료되었거나 유효하지 않음
- 로그아웃 후 재로그인

### Tailwind 스타일이 적용되지 않음
- `npm run build`로 재빌드
- 브라우저 캐시 클리어

## 📚 참고 자료

- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

## 👥 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.
