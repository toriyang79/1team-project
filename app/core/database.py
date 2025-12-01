"""
데이터베이스 연결 및 세션 관리

SQLAlchemy 2.0의 비동기(async) 패턴을 사용합니다.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
# Base 클래스는 models.base에서 import
from app.models.base import Base

# ===== 모델 Import (테이블 생성을 위해 필요) =====
# 모든 모델을 import하여 Base.metadata에 등록되도록 함
from app.models.image_post import ImagePost  # noqa: F401
from app.models.image_like import ImageLike  # noqa: F401
from app.models.tournament_vote import TournamentVote  # noqa: F401

# ===== 비동기 엔진 생성 =====
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # DEBUG 모드에서 SQL 로깅
    future=True,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_size=10,  # 연결 풀 크기
    max_overflow=20,  # 최대 추가 연결 수
)

# ===== 비동기 세션 팩토리 =====
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 커밋 후에도 객체 접근 가능
    autocommit=False,
    autoflush=False,
)


# ===== 의존성: 데이터베이스 세션 제공 =====
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션을 제공하는 의존성 함수입니다.

    FastAPI의 Depends()와 함께 사용됩니다.

    Example:
        ```python
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # db 세션 사용
            pass
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ===== 데이터베이스 초기화 함수 =====
async def init_db() -> None:
    """
    데이터베이스 테이블을 생성합니다.

    주의: 운영 환경에서는 Alembic 마이그레이션을 사용하세요.
    이 함수는 개발 초기 단계에서만 사용하는 것을 권장합니다.
    """
    async with engine.begin() as conn:
        # 모든 테이블 생성
        await conn.run_sync(Base.metadata.create_all)


# ===== 데이터베이스 정리 함수 =====
async def close_db() -> None:
    """
    데이터베이스 연결을 종료합니다.

    애플리케이션 종료 시 호출됩니다.
    """
    await engine.dispose()
