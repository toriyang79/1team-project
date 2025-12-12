
# https://www.artlion.p-e.kr/
# http://43.200.134.109:5173/
🦁 ArtLion — 당신의 창작이 한계를 넘는 순간

**ArtLion(아트라이언)**은 AI로 만들어진 이미지·음악·영상을 누구나 자유롭게 공유하고 즐길 수 있는 크리에이티브 플랫폼입니다.
복잡한 도구 없이, 영감이 떠오르는 그대로 업로드하고 교류하며, 전 세계 사용자들과 새로운 형태의 창작 문화를 만들어갑니다.

AI가 만든 작품이 한곳에 모이고, 작품으로 연결된 사람들이 서로에게 영감이 되고,
그 안에서 완전히 새로운 창작의 생태계가 태어납니다.

ArtLion — 창작을 더 쉽고, 더 자유롭고, 더 강렬하게.
이곳에서 당신의 상상이 작품이 됩니다.

---

# 시연 영상
https://youtu.be/PfsTYSn6KZE

# 프론트 엔드 깃허브 링크
https://github.com/toriyang79/1team-project-FE/tree/develop

# 개발 일지
https://cheerful-allium-382.notion.site/20251212-2c7eafdfc3c78024b7badfc70bc14503?source=copy_link

---

# 김미숙 담당 파트 소개

# AI Image Community API
FastAPI 기반의 AI 이미지 커뮤니티 서비스를 담당했습니다.

# http://13.125.57.129:8000/docs
다음 URL에서 API문서를 확인할 수 있습니다.



## 🎯 프로젝트 개요

AI로 생성한 이미지를 공유하고, 좋아요를 누르고, 토너먼트를 통해 경쟁하는 커뮤니티 제작.

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

## 📋 개발 단계 (Phases)

- [x] **Phase 1**: 프로젝트 초기 설정
- [ ] **Phase 2**: 데이터베이스 모델 설계
- [ ] **Phase 3**: JWT 인증 구현
- [ ] **Phase 4**: 이미지 CRUD API
- [ ] **Phase 5**: 피드 기능
- [ ] **Phase 6**: 좋아요 기능
- [ ] **Phase 7**: 토너먼트 기능
- [ ] **Phase 8**: Docker 배포

```

## 📝 API 엔드포인트 



### 이미지
- `POST /api-image/v1/images/` - 이미지 업로드
- `GET /api-image/v1/images/{id}` - 이미지 조회
- `PUT /api-image/v1/images/{id}` - 이미지 수정
- `DELETE /api-image/v1/images/{id}` - 이미지 삭제
- `GET /api-image/v1/images/random` - 랜덤 피드
- `GET /api-image/v1/images/top-24h` - 인기 Top 10

### 좋아요
- `POST /api-image/v1/images/{id}/like` - 좋아요 추가
- `DELETE /api-image/v1/images/{id}/like` - 좋아요 취소

### 토너먼트
- `GET /api-image/v1/tournaments/match` - 랜덤 매치업
- `POST /api-image/v1/tournaments/vote` - 투표

