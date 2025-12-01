"""
이미지 좋아요 모델

이미지에 대한 사용자의 좋아요를 저장합니다.
"""

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ImageLike(Base, TimestampMixin):
    """
    이미지 좋아요 모델

    사용자가 이미지에 누른 좋아요를 관리합니다.
    한 사용자는 같은 이미지에 한 번만 좋아요를 누를 수 있습니다 (UNIQUE 제약).
    """
    __tablename__ = "image_likes"

    # ===== 기본 필드 =====
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="좋아요 ID"
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="좋아요를 누른 사용자 ID"
    )

    image_post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("image_posts.id", ondelete="CASCADE"),
        nullable=False,
        comment="좋아요가 눌린 이미지 게시물 ID"
    )

    # ===== 관계 설정 =====
    image_post: Mapped["ImagePost"] = relationship(
        "ImagePost",
        back_populates="likes"
    )

    # ===== 제약조건 및 인덱스 =====
    __table_args__ = (
        # 한 사용자는 같은 이미지에 한 번만 좋아요 가능
        UniqueConstraint("user_id", "image_post_id", name="uq_user_image_like"),
        # 인덱스 설정
        Index("idx_image_post_id", "image_post_id"),
        Index("idx_user_id_like", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<ImageLike(id={self.id}, user_id={self.user_id}, image_post_id={self.image_post_id})>"
