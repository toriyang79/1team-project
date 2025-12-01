"""
토너먼트 투표 모델

이미지 토너먼트의 투표 기록을 저장합니다.
"""

from sqlalchemy import Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TournamentVote(Base, TimestampMixin):
    """
    토너먼트 투표 모델

    두 이미지가 대결했을 때, 어떤 이미지가 승리했는지 기록합니다.
    승리한 이미지의 tournament_win_count가 증가합니다.
    """
    __tablename__ = "tournament_votes"

    # ===== 기본 필드 =====
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="투표 ID"
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="투표한 사용자 ID"
    )

    winner_image_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("image_posts.id", ondelete="CASCADE"),
        nullable=False,
        comment="승리한 이미지 ID"
    )

    loser_image_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("image_posts.id", ondelete="CASCADE"),
        nullable=False,
        comment="패배한 이미지 ID"
    )

    # ===== 인덱스 설정 =====
    __table_args__ = (
        Index("idx_winner_image_id", "winner_image_id"),
        Index("idx_loser_image_id", "loser_image_id"),
        Index("idx_user_id_vote", "user_id"),
        Index("idx_created_at_vote", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<TournamentVote(id={self.id}, "
            f"winner={self.winner_image_id}, "
            f"loser={self.loser_image_id})>"
        )
