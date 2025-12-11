# AI Image Community API

FastAPI 기반의 AI 이미지 커뮤니티 서비스입니다.

## 🎯 프로젝트 개요

AI로 생성한 이미지를 공유하고, 좋아요를 누르고, 토너먼트를 통해 경쟁하는 커뮤니티 플랫폼입니다.

## 🛠 기술 스택

- **Python 3.12+**
- **FastAPI** - 비동기 웹 프레임워크
- **SQLAlchemy 2.0** - 비동기 ORM
- **PostgreSQL** - 데이터베이스
- **JWT (RS256)** - 인증 (Django Auth 서버와 공유)
- **Docker & Docker Compose** - 컨테이너화

## 📁 프로젝트 구조

```
├── app/
│   ├── core/           # 핵심 설정 (config, database, security)
│   ├── models/         # SQLAlchemy 모델
│   ├── schemas/        # Pydantic 스키마
│   ├── api/v1/         # API 라우터
│   ├── services/       # 비즈니스 로직
│   └── utils/          # 유틸리티
├── uploads/            # 업로드된 이미지 저장
├── tests/              # 테스트 코드
├── main.py             # FastAPI 앱 진입점
├── requirements.txt    # Python 의존성
├── docker-compose.yml  # Docker 설정
└── .env                # 환경변수
```

## 🚀 시작하기

### 1. 저장소 클론 및 의존성 설치

```bash
# 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값을 설정하세요.

```bash
cp .env.example .env
```

#### JWT Public Key 설정 (임시 개발용)

개발용 임시 키를 생성하려면:

```bash
# cryptography 패키지 설치 (requirements.txt에 포함되어 있음)
pip install cryptography

# JWT 키 페어 생성
python generate_jwt_keys.py
```

생성된 `jwt_public_key.pem`의 내용을 `.env` 파일의 `JWT_PUBLIC_KEY`에 복사하세요.

⚠️ **운영 환경에서는 Django Auth 서버에서 제공하는 실제 Public Key를 사용해야 합니다!**

### 3. 데이터베이스 실행

Docker Compose를 사용하여 PostgreSQL을 실행합니다.

```bash
docker-compose up -d postgres
```

데이터베이스 연결 확인:

```bash
docker-compose logs postgres
```

### 4. 애플리케이션 실행

#### 로컬에서 직접 실행 (개발 모드)

```bash
# uvicorn으로 직접 실행 (리로드 활성화)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는 Python으로 실행
python main.py
```

#### Docker로 실행

```bash
docker-compose up --build
```

### 5. API 문서 확인

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📋 개발 단계 (Phases)

- [x] **Phase 1**: 프로젝트 초기 설정
- [ ] **Phase 2**: 데이터베이스 모델 설계
- [ ] **Phase 3**: JWT 인증 구현
- [ ] **Phase 4**: 이미지 CRUD API
- [ ] **Phase 5**: 피드 기능
- [ ] **Phase 6**: 좋아요 기능
- [ ] **Phase 7**: 토너먼트 기능
- [ ] **Phase 8**: Docker 배포

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app --cov-report=html
```

## 📝 API 엔드포인트 (예정)

### 인증
- `POST /api/v1/auth/verify` - JWT 토큰 검증

### 이미지
- `POST /api/v1/images/` - 이미지 업로드
- `GET /api/v1/images/{id}` - 이미지 조회
- `PUT /api/v1/images/{id}` - 이미지 수정
- `DELETE /api/v1/images/{id}` - 이미지 삭제
- `GET /api/v1/images/random` - 랜덤 피드
- `GET /api/v1/images/top-24h` - 인기 Top 10

### 좋아요
- `POST /api/v1/images/{id}/like` - 좋아요 추가
- `DELETE /api/v1/images/{id}/like` - 좋아요 취소

### 토너먼트
- `GET /api/v1/tournaments/match` - 랜덤 매치업
- `POST /api/v1/tournaments/vote` - 투표

## 🔐 개발용 토큰 발급 라우트 안전하게 쓰기

- 이 프로젝트에는 개발 편의를 위한 토큰 발급 라우트가 있습니다: `POST /api/v1/auth-test/generate-token`
- 이 라우트는 기본적으로 비활성화되어 있으며, 로컬 개발에서만 켤 수 있습니다.

사용 방법(아주 쉽게):
- 1) `.env`에서 `ENABLE_DEV_AUTH=true`가 되어 있는지 확인합니다. 운영에서는 반드시 `false` 또는 미설정!
- 2) 서버를 실행하고, Swagger(`/docs`)로 들어갑니다.
- 3) `POST /api/v1/auth-test/generate-token`에 `user_id`를 넣고 실행해서 `access_token`을 받습니다.
- 4) Swagger 오른쪽 위의 Authorize 버튼을 눌러 토큰만 붙여넣습니다. ("Bearer "는 쓰지 않아요)
- 5) 이제 인증이 필요한 API(예: 이미지 업로드)를 테스트할 수 있어요.

안전 수칙:
- 운영 배포에서는 `.env`에 `ENABLE_DEV_AUTH`를 켜지 마세요.
- 운영에서는 `DEBUG=False`, `JWT_PRIVATE_KEY`는 절대 넣지 마세요(발급 서버에만 보관).
- `JWT_PUBLIC_KEY`만 이 서비스에 주입해서 토큰을 검증하세요.

## 📚 추가 문서

- [DB_MODELS.md](./.claude/skills/fastapi-image-community/resources/DB_MODELS.md) - 데이터베이스 모델 상세
- [API_SPEC.md](./.claude/skills/fastapi-image-community/resources/API_SPEC.md) - API 명세
- [DEPLOYMENT.md](./.claude/skills/fastapi-image-community/resources/DEPLOYMENT.md) - 배포 가이드

## ☁️ EC2에서 S3 업로드가 안 될 때 (IAM Role 사용 권장)

프로덕션 `compose.yaml`은 기본적으로 AWS 액세스 키를 주입하지 않고, EC2 인스턴스의 IAM Role(Instance Profile)을 통해
컨테이너 내부의 boto3가 자동으로 자격 증명을 가져오도록 설계되어 있습니다. 다음 순서대로 설정하세요.

1) IAM Role 생성 및 권한 부여
- 콘솔: IAM → Roles → Create role → Trusted entity: EC2
- 권한 정책: 최소 권한 예시
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject","s3:PutObjectAcl","s3:GetObject","s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR_S3_BUCKET/*"
    }
  ]
}
```

2) EC2 인스턴스에 Role 연결
- EC2 → Instances → 대상 인스턴스 → Actions → Security → Modify IAM role → 위에서 만든 Role 선택

3) 애플리케이션 환경 변수 점검
- `compose.yaml`의 `fastapi.environment`에 다음 필수 값 설정
  - `STORAGE_BACKEND=s3`
  - `AWS_REGION`, `AWS_S3_BUCKET`, (선택) `AWS_S3_PUBLIC_URL`, `AWS_S3_PREFIX`
- 액세스 키(`AWS_ACCESS_KEY_ID/SECRET`)는 설정하지 않습니다. (IAM Role이 대체)

4) 네트워크/SSL 확인
- 컨테이너가 인스턴스 메타데이터(169.254.169.254)에 접근 가능해야 합니다(기본 허용).
- Dockerfile에 `ca-certificates` 설치(본 저장소 반영됨)로 S3 HTTPS 통신 신뢰성 확보.

5) 재배포
```bash
docker compose -f compose.yaml up -d --build
```

문제가 계속되면 S3 버킷 정책/퍼블릭 접근 설정, 그리고 버킷의 Bucket Owner Enforced(ACL 금지) 여부를 확인하세요.
코드는 ACL 에러가 발생 시 자동으로 ACL 없이 재시도합니다.

## 🤝 기여

프로젝트에 기여하고 싶으시다면 Pull Request를 보내주세요!

## 📄 라이선스

MIT License
