"""
애플리케이션 생명주기 관리

FastAPI의 lifespan 이벤트를 사용하여
애플리케이션 시작 및 종료 시 필요한 작업을 수행합니다.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import init_db, close_db
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 컨텍스트 매니저

    시작 시:
        - 업로드 디렉토리 생성
        - 데이터베이스 테이블 초기화 (개발 환경)

    종료 시:
        - 데이터베이스 연결 종료
    """
    # ===== 시작 시 실행 =====
    print("=" * 60)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 시작 중...")
    print("=" * 60)

    # 업로드 디렉토리 생성 (로컬 스토리지일 때만)
    import os
    if settings.STORAGE_BACKEND.lower() == "local":
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        print(f"✅ 업로드 디렉토리 생성: {settings.UPLOAD_DIR}")
    else:
        print("ℹ️  S3 스토리지 사용: 로컬 업로드 디렉토리 생성 생략")

    # 데이터베이스 초기화 (개발 환경에서만)
    if settings.DEBUG:
        try:
            await init_db()
            print("✅ 데이터베이스 테이블 초기화 완료")
        except Exception as e:
            print(f"⚠️  데이터베이스 초기화 실패: {e}")
    else:
        print("ℹ️  운영 환경: Alembic 마이그레이션을 사용하세요")

    print("=" * 60)
    print(f"✅ 서버 준비 완료: http://{settings.HOST}:{settings.PORT}")
    print("=" * 60)

    yield  # 애플리케이션 실행

    # ===== 종료 시 실행 =====
    print("\n" + "=" * 60)
    print("🛑 애플리케이션 종료 중...")
    print("=" * 60)

    # 데이터베이스 연결 종료
    await close_db()
    print("✅ 데이터베이스 연결 종료")

    print("=" * 60)
    print("👋 애플리케이션 종료 완료")
    print("=" * 60)
