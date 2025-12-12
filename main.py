"""
FastAPI AI 이미지 커뮤니티 API

메인 진입점 파일입니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, CORS_ALLOWED_ORIGINS
from app.core.lifespan import lifespan

# ===== FastAPI 앱 생성 =====
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI로 생성한 이미지를 공유하고 토너먼트로 경쟁하는 커뮤니티 API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,  # 생명주기 관리
)

# ===== CORS 설정 =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 정적 파일 서빙 (업로드된 이미지, 로컬 스토리지일 때만) =====
import os

# 로컬 디스크를 사용할 때만 /uploads를 정적 마운트합니다.
if settings.STORAGE_BACKEND.lower() == "local":
    # uploads 디렉토리가 없으면 생성
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 정적 파일 마운트 (uploads 전체 디렉토리)
    uploads_root = "./uploads"
    if os.path.exists(uploads_root):
        app.mount(
            "/uploads",
            StaticFiles(directory=uploads_root),
            name="uploads"
        )

# ===== 라우터 등록 =====
from app.api.v1.router import api_v1_router
app.include_router(api_v1_router, prefix="/api-image/v1")


# ===== 헬스 체크 엔드포인트 =====
@app.get("/", tags=["Health"])
async def root():
    """
    루트 엔드포인트

    API 상태를 확인합니다.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트

    서버가 정상적으로 실행 중인지 확인합니다.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ===== 개발 서버 실행 (직접 실행 시) =====
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
