"""
API v1 통합 라우터

모든 v1 API 라우터를 통합합니다.
"""

from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.images import router as images_router
from app.api.v1.likes import router as likes_router
from app.api.v1.tournaments import router as tournaments_router

# v1 통합 라우터
api_v1_router = APIRouter()

# 이미지 라우터 등록
api_v1_router.include_router(images_router)

# 좋아요 라우터 등록
api_v1_router.include_router(likes_router)

# 토너먼트 라우터 등록
api_v1_router.include_router(tournaments_router)

# 테스트용 인증 라우터 (개발 환경 전용)
if settings.DEBUG and settings.ENABLE_DEV_AUTH:
    from app.api.v1.auth_test import router as auth_test_router
    api_v1_router.include_router(auth_test_router)
