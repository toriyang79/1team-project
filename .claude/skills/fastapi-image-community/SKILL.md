---
name: fastapi-ai-image-community
description: |
  FastAPI 기반 AI 이미지 커뮤니티 서비스 개발 가이드 스킬. 
  이 스킬은 팀 프로젝트의 일부로서 AI 이미지 공유/토너먼트 플랫폼을 구축할 때 사용합니다.
  Django Auth 서버의 JWT를 검증하고, PostgreSQL을 공유하며, 독립적인 FastAPI 서버로 운영됩니다.
  사용자가 AI 이미지 커뮤니티, FastAPI 백엔드, 토너먼트 시스템, 
  이미지 CRUD API를 개발하려 할 때 이 스킬을 활용합니다.
---

# FastAPI AI 이미지 커뮤니티 개발 스킬

이 스킬은 **AI 이미지 커뮤니티 서비스**를 FastAPI로 개발하기 위한 체계적인 가이드입니다.

## 🎯 스킬 목표

팀 프로젝트의 일환으로, JWT 인증을 공유하는 독립 FastAPI 서버 기반의 AI 이미지 커뮤니티를 구축합니다.

---

## 📋 개발 원칙

### 1. 대화형 요구사항 수집
- 서비스 제안을 받으면 **질문을 통해 요구사항을 수집**합니다
- 모호한 부분은 반드시 확인 질문을 합니다
- 다음 사항들을 반드시 확인합니다:
  - 이미지 저장 방식 (로컬/S3)
  - 파일 크기 제한
  - 토너먼트 세부 규칙
  - 배포 환경 상세

### 2. 사용자 주도 터미널 작업
- **터미널 명령어는 제시만** 하고, 실제 실행은 사용자가 합니다
- 복사-붙여넣기 가능한 형태로 명령어를 제공합니다
- 예시:
  ```bash
  # 아래 명령어를 터미널에서 실행해주세요
  pip install \
  fastapi[standard] \
  sqlalchemy[asyncio] \
  asyncpg \
  python-jose[cryptography] \
  bcrypt \
  python-dotenv \
  aiofiles \
  python-multipart \
  pydantic-settings

  ```

### 3. 테스트 가이드 제공
- 테스트 **방식과 시나리오를 제시**하고, 실제 테스트는 사용자가 수행합니다
- 테스트 결과를 공유받아 다음 단계로 진행합니다
- 예시:
  ```
  📝 테스트 시나리오:
  1. POST /api/images/ 로 이미지 업로드 테스트
  2. Authorization 헤더에 JWT 토큰 포함
  3. 예상 응답: 201 Created
  
  테스트 완료 후 결과를 알려주세요.
  ```

### 4. 단계별 승인 진행
- 각 작업 단계는 **사용자 승인 후에만** 다음으로 진행합니다
- Phase 완료 시 체크리스트와 함께 승인 요청합니다
- 예시:
  ```
  ✅ Phase 1 완료 체크리스트:
  - [ ] 프로젝트 구조 생성 확인
  - [ ] 가상환경 활성화 확인
  - [ ] 의존성 설치 완료 확인
  
  위 항목들 확인 후 승인해주시면 Phase 2로 진행하겠습니다.
  ```

---

## 🛠 기술 스택 명세

### 필수 기술
| 기술 | 버전/설명 |
|------|---------|
| Python | 3.12+ |
| FastAPI | standard 최신 버전 |
| SQLAlchemy | 2.0+ (async 문법 필수) |
| PostgreSQL | 공유 DB (팀 공통) |
| JWT | RS256 비대칭키 (public key 검증) |
| Pydantic | v2+ (필드 검증) |

### 핵심 라이브러리
```
fastapi[standard]
sqlalchemy[asyncio]
asyncpg                      # PostgreSQL async 드라이버
python-jose[cryptography]    # JWT 검증 (RS256 지원)
bcrypt                       # 비밀번호 (필요시)
python-dotenv                # 환경변수 관리
aiofiles                     # 비동기 파일 처리
python-multipart             # 파일 업로드 처리
pydantic-settings            # 환경변수 설정 관리
```

---

## 📁 프로젝트 디렉토리 구조

```
project-root/
├── main.py                      # FastAPI 앱 진입점 (lifespan 포함)
├── .env                         # 환경변수 (git에서 제외)
├── .env.example                 # 환경변수 템플릿
├── requirements.txt             # 의존성 목록
├── Dockerfile                   # Docker 설정
├── docker-compose.yml           # Docker Compose 설정
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/                    # 핵심 설정
│   │   ├── __init__.py
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # DB 연결, 세션 관리
│   │   ├── security.py          # JWT 검증, 의존성
│   │   └── lifespan.py          # 앱 생명주기 관리
│   │
│   ├── models/                  # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── base.py              # Base 클래스
│   │   ├── image_post.py        # 이미지 게시물 모델
│   │   ├── image_like.py        # 좋아요 모델
│   │   └── tournament_vote.py   # 토너먼트 투표 모델
│   │
│   ├── schemas/                 # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── image.py             # 이미지 요청/응답 분리
│   │   ├── like.py              # 좋아요 스키마
│   │   ├── tournament.py        # 토너먼트 스키마
│   │   └── common.py            # 공통 응답 스키마
│   │
│   ├── api/                     # API 라우터
│   │   ├── __init__.py
│   │   ├── deps.py              # 공통 의존성
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # v1 통합 라우터
│   │       ├── images.py        # 이미지 CRUD 엔드포인트
│   │       ├── likes.py         # 좋아요 엔드포인트
│   │       └── tournaments.py   # 토너먼트 엔드포인트
│   │
│   ├── services/                # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── image_service.py
│   │   ├── like_service.py
│   │   └── tournament_service.py
│   │
│   └── utils/                   # 유틸리티
│       ├── __init__.py
│       ├── file_handler.py      # 비동기 파일 처리
│       └── validators.py        # 파일 검증
│
├── uploads/                     # 업로드 파일 저장 (개발용)
│   └── images/
│
└── tests/                       # 테스트 코드
    ├── __init__.py
    ├── conftest.py
    └── api/
        └── test_images.py
```

---

## 🔐 JWT 인증 구현 가이드

### RS256 Public Key 검증 방식

Django Auth 서버에서 private key로 서명한 JWT를 FastAPI에서 public key로 검증합니다.

```python
# app/core/security.py
from typing import Optional
from jose import jwt, JWTError  # python-jose 라이브러리
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    JWT 토큰을 검증하고 사용자 정보를 반환합니다.
    
    - RS256 알고리즘 사용 (비대칭키)
    - Django Auth 서버의 public key로 검증
    - python-jose 라이브러리 사용
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: Optional[int] = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return {"user_id": user_id, "payload": payload}
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )
```

### 환경변수 설정 (.env)
```env
# JWT 설정 (Django Auth 서버에서 제공받은 Public Key)
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
-----END PUBLIC KEY-----"
JWT_ALGORITHM=RS256

# 데이터베이스 (팀 공유)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/team_db

# 파일 업로드
UPLOAD_DIR=./uploads/images
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=["jpg","jpeg","png","gif","webp"]  # JSON 배열 형식
```

### Settings 클래스 (pydantic-settings)

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    # JWT
    JWT_PUBLIC_KEY: str
    JWT_ALGORITHM: str = "RS256"
    
    # Database
    DATABASE_URL: str
    
    # File Upload
    UPLOAD_DIR: str = "./uploads/images"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    
    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        """문자열 또는 JSON 배열을 list로 변환"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # 콤마 구분 문자열 폴백
                return [ext.strip() for ext in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## 📊 SQLAlchemy 2.0 모델 가이드

### 기본 모델 구조

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now()
    )
```

### 이미지 게시물 모델

```python
# app/models/image_post.py
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin

class ImagePost(Base, TimestampMixin):
    __tablename__ = "image_posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    image_url: Mapped[str] = mapped_column(String(500))
    prompt: Mapped[str] = mapped_column(Text)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_tournament_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 관계 설정
    likes: Mapped[List["ImageLike"]] = relationship(
        back_populates="image_post",
        cascade="all, delete-orphan"
    )
```

---

## 📝 Pydantic 스키마 가이드

### 요청/응답 스키마 분리 원칙

```python
# app/schemas/image.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# === 요청 스키마 ===
class ImageCreateRequest(BaseModel):
    """이미지 업로드 요청"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="AI 생성 프롬프트")
    model_name: Optional[str] = Field(None, max_length=100, description="사용한 AI 모델명")
    is_tournament_opt_in: bool = Field(False, description="토너먼트 참여 여부")

class ImageUpdateRequest(BaseModel):
    """이미지 수정 요청"""
    prompt: Optional[str] = Field(None, min_length=1, max_length=2000)
    model_name: Optional[str] = Field(None, max_length=100)
    is_tournament_opt_in: Optional[bool] = None

# === 응답 스키마 ===
class ImageResponse(BaseModel):
    """이미지 단일 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    image_url: str
    prompt: str
    model_name: Optional[str]
    is_tournament_opt_in: bool
    created_at: datetime
    like_count: int = 0
    tournament_win_count: int = 0

class ImageListResponse(BaseModel):
    """이미지 목록 응답"""
    items: list[ImageResponse]
    total: int
    page: int
    size: int
```

---

## 📡 API 엔드포인트 명세

### OpenAPI 문서화 가이드

각 엔드포인트에 상세한 설명을 포함합니다:

```python
# app/api/v1/images.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/images", tags=["Images"])

@router.post(
    "/",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI 이미지 업로드",
    description="""
    AI로 생성한 이미지를 업로드합니다.
    
    ## 최종 경로
    `POST /api/v1/images/`
    
    ## 요청 조건
    - **인증 필수**: JWT 토큰이 Authorization 헤더에 포함되어야 합니다
    - **파일 제한**: 최대 10MB, jpg/jpeg/png/gif/webp 형식만 허용
    
    ## 응답
    - **201**: 업로드 성공, 생성된 이미지 정보 반환
    - **400**: 잘못된 파일 형식 또는 크기 초과
    - **401**: 인증 실패
    """,
    responses={
        201: {"description": "이미지 업로드 성공"},
        400: {"description": "잘못된 요청 (파일 형식/크기 오류)"},
        401: {"description": "인증 필요"},
    }
)
async def create_image(
    file: UploadFile = File(..., description="업로드할 이미지 파일"),
    prompt: str = Form(..., description="AI 생성 프롬프트"),
    model_name: str | None = Form(None, description="사용한 AI 모델명"),
    is_tournament_opt_in: bool = Form(False, description="토너먼트 참여 여부"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """AI 이미지를 업로드하고 메타데이터를 저장합니다."""
    pass
```

### 라우터 통합 (main.py)

```python
# main.py
from fastapi import FastAPI
from app.api.v1.router import api_v1_router

app = FastAPI(title="AI Image Community API")

# 모든 v1 API는 /api/v1 prefix로 통합
app.include_router(api_v1_router, prefix="/api/v1")
```

---

## 📤 비동기 파일 업로드 가이드

### 청크 단위 저장 + 검증

```python
# app/utils/file_handler.py
import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

CHUNK_SIZE = 1024 * 1024  # 1MB

async def validate_and_save_file(file: UploadFile) -> str:
    """
    파일을 검증하고 비동기로 저장합니다.
    
    검증 항목:
    1. 파일 확장자 검증
    2. 파일 크기 제한 (청크 단위로 체크)
    3. 안전한 파일명 생성
    """
    # 1. 확장자 검증
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않는 파일 형식입니다. 허용: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # 2. 안전한 파일명 생성
    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # 3. 청크 단위 비동기 저장 + 크기 검증
    total_size = 0
    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(CHUNK_SIZE):
            total_size += len(chunk)
            if total_size > settings.MAX_FILE_SIZE:
                # 초과 시 파일 삭제
                await out_file.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"파일 크기가 {settings.MAX_FILE_SIZE // (1024*1024)}MB를 초과했습니다."
                )
            await out_file.write(chunk)
    
    return f"/uploads/images/{safe_filename}"
```

---

## 🔄 개발 단계 (Phases)

### Phase 1: 프로젝트 초기 설정
- [ ] 프로젝트 디렉토리 구조 생성
- [ ] 가상환경 생성 및 의존성 설치
- [ ] .env 파일 구성
- [ ] 기본 FastAPI 앱 설정 (main.py + lifespan)

### Phase 2: 데이터베이스 설정
- [ ] SQLAlchemy 2.0 async 엔진 설정
- [ ] Base 모델 및 세션 관리 구현
- [ ] 모든 테이블 모델 정의 (image_posts, image_likes, tournament_votes)
- [ ] 마이그레이션 또는 테이블 생성 확인

### Phase 3: JWT 인증 구현
- [ ] Public Key 설정 및 로드
- [ ] JWT 검증 의존성 구현
- [ ] 인증 테스트

### Phase 4: 이미지 CRUD API
- [ ] 파일 업로드 유틸리티 구현 (검증 + 비동기 저장)
- [ ] 이미지 생성 API (POST /api/v1/images/)
- [ ] 이미지 조회 API (GET /api/v1/images/{id})
- [ ] 이미지 수정 API (PUT /api/v1/images/{id})
- [ ] 이미지 삭제 API (DELETE /api/v1/images/{id})

### Phase 5: 피드 기능
- [ ] 랜덤 피드 API (GET /api/v1/images/random)
- [ ] 인기 Top 10 API (GET /api/v1/images/top-24h)

### Phase 6: 좋아요 기능
- [ ] 좋아요 추가 API (POST /api/v1/images/{id}/like)
- [ ] 좋아요 취소 API (DELETE /api/v1/images/{id}/like)
- [ ] UNIQUE 제약조건 처리

### Phase 7: 토너먼트 기능
- [ ] 랜덤 매치업 API (GET /api/v1/tournaments/match)
- [ ] 투표 API (POST /api/v1/tournaments/vote)
- [ ] 랭킹 연동 (승리 시 점수 반영)

### Phase 8: Docker 배포 준비
- [ ] Dockerfile 작성
- [ ] docker-compose.yml 작성
- [ ] 환경별 설정 분리

---

## ⚠️ 주의사항 및 베스트 프랙티스

### SQLAlchemy 2.0 문법 필수
```python
# ❌ 1.x 스타일 (사용 금지)
session.query(ImagePost).filter_by(id=1).first()

# ✅ 2.0 스타일 (필수)
from sqlalchemy import select
stmt = select(ImagePost).where(ImagePost.id == 1)
result = await session.execute(stmt)
image = result.scalar_one_or_none()
```

### 트랜잭션 처리
```python
async def create_with_transaction(db: AsyncSession, data: dict):
    async with db.begin():
        # 트랜잭션 내 모든 작업
        new_item = ImagePost(**data)
        db.add(new_item)
        await db.flush()  # ID 생성을 위해 flush
        await db.refresh(new_item)
    return new_item
```

### REST API 원칙 준수
- GET: 조회 (멱등성 보장)
- POST: 생성 (201 Created 반환)
- PUT: 전체 수정
- PATCH: 부분 수정
- DELETE: 삭제 (204 No Content 또는 200 OK)

---

## 📚 참고 문서

추가 상세 내용은 아래 파일들을 참조하세요:

- [DB_MODELS.md](./resources/DB_MODELS.md) - 상세 모델 정의
- [API_SPEC.md](./resources/API_SPEC.md) - 전체 API 명세
- [DEPLOYMENT.md](./resources/DEPLOYMENT.md) - 배포 가이드