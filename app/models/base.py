"""
SQLAlchemy Base 클래스 및 공통 Mixin

모든 모델의 기반이 되는 Base 클래스와
재사용 가능한 Mixin을 정의합니다.
"""

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """모든 모델의 기본 클래스"""
    pass


class TimestampMixin:
    """
    생성일시/수정일시 자동 관리 Mixin

    이 Mixin을 상속받으면 created_at과 updated_at 필드가 자동으로 추가됩니다.
    """
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="생성일시"
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정일시"
    )
