"""
이미지 게시물 모델

AI로 생성한 이미지 게시물을 저장합니다.
"""

from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ImagePost(Base, TimestampMixin):
    """
    AI 이미지 게시물 모델

    사용자가 업로드한 AI 생성 이미지의 메타데이터를 저장합니다.
    """
    __tablename__ = "image_posts"

    # ===== 기본 필드 =====
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="이미지 게시물 ID"
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="작성자 ID (Django Auth 서버의 사용자 ID)"
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="이미지 파일 URL"
    )

    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="AI 생성 프롬프트"
    )

    model_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="사용한 AI 모델명 (예: DALL-E, Midjourney, Stable Diffusion)"
    )

    # ===== 토너먼트 관련 =====
    is_tournament_opt_in: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        comment="토너먼트 참여 여부"
    )

    tournament_win_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        comment="토너먼트 승리 횟수"
    )

    # ===== 상태 관리 =====
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
        comment="활성 상태 (삭제 시 False)"
    )

    # ===== 관계 설정 =====
    likes: Mapped[List["ImageLike"]] = relationship(
        "ImageLike",
        back_populates="image_post",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # ===== 인덱스 설정 =====
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_tournament_opt_in", "is_tournament_opt_in"),
        Index("idx_created_at", "created_at"),
        Index("idx_active_created", "is_active", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ImagePost(id={self.id}, user_id={self.user_id}, prompt='{self.prompt[:30]}...')>"

    @property
    def like_count(self) -> int:
        """좋아요 개수를 반환합니다."""
        return len(self.likes) if self.likes else 0
