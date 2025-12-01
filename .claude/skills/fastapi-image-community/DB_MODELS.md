# 데이터베이스 모델 상세 정의

이 문서는 AI 이미지 커뮤니티의 데이터베이스 모델을 상세히 정의합니다.

---

## 📊 ERD (Entity Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                         image_posts                              │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                  │ SERIAL                               │
│ user_id                  │ INTEGER (JWT에서 추출)                │
│ image_url                │ VARCHAR(500)                         │
│ prompt                   │ TEXT                                  │
│ model_name               │ VARCHAR(100) NULLABLE                 │
│ is_tournament_opt_in     │ BOOLEAN DEFAULT FALSE                 │
│ is_active                │ BOOLEAN DEFAULT TRUE                  │
│ created_at               │ TIMESTAMP DEFAULT NOW()               │
└─────────────────────────────────────────────────────────────────┘
          │
          │ 1:N
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         image_likes                              │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                  │ SERIAL                               │
│ user_id                  │ INTEGER                               │
│ image_post_id (FK)       │ INTEGER → image_posts.id              │
│ created_at               │ TIMESTAMP DEFAULT NOW()               │
├─────────────────────────────────────────────────────────────────┤
│ UNIQUE CONSTRAINT: (user_id, image_post_id)                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       tournament_votes                           │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                  │ SERIAL                               │
│ match_id                 │ VARCHAR(36) - UUID                    │
│ voter_id                 │ INTEGER                               │
│ winner_image_id (FK)     │ INTEGER → image_posts.id              │
│ loser_image_id (FK)      │ INTEGER → image_posts.id              │
│ created_at               │ TIMESTAMP DEFAULT NOW()               │
├─────────────────────────────────────────────────────────────────┤
│ CHECK CONSTRAINT: winner_image_id <> loser_image_id             │
│ INDEX: (voter_id, match_id) - 중복 투표 방지용                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗃 전체 모델 코드

### Base 모델 및 Mixin

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """SQLAlchemy 2.0 Base 클래스"""
    pass

class TimestampMixin:
    """생성 시간 자동 기록 Mixin"""
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        nullable=False
    )
```

### ImagePost 모델

```python
# app/models/image_post.py
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.image_like import ImageLike
    from app.models.tournament_vote import TournamentVote

class ImagePost(Base, TimestampMixin):
    """
    AI 이미지 게시물 모델
    
    사용자가 업로드한 AI 생성 이미지와 관련 메타데이터를 저장합니다.
    """
    __tablename__ = "image_posts"
    __table_args__ = (
        Index("ix_image_posts_user_id", "user_id"),
        Index("ix_image_posts_created_at", "created_at"),
        Index("ix_image_posts_tournament_opt_in", "is_tournament_opt_in"),
    )
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 외래키 없이 user_id만 저장 (Django Auth 서버 참조)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # 이미지 정보
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 상태 플래그
    is_tournament_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 관계 설정
    likes: Mapped[List["ImageLike"]] = relationship(
        "ImageLike",
        back_populates="image_post",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # 승리한 토너먼트
    won_tournaments: Mapped[List["TournamentVote"]] = relationship(
        "TournamentVote",
        foreign_keys="TournamentVote.winner_image_id",
        back_populates="winner_image",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # 패배한 토너먼트
    lost_tournaments: Mapped[List["TournamentVote"]] = relationship(
        "TournamentVote",
        foreign_keys="TournamentVote.loser_image_id",
        back_populates="loser_image",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<ImagePost(id={self.id}, user_id={self.user_id})>"
```

### ImageLike 모델

```python
# app/models/image_like.py
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.image_post import ImagePost

class ImageLike(Base, TimestampMixin):
    """
    이미지 좋아요 모델
    
    한 사용자가 한 이미지에 한 번만 좋아요를 누를 수 있습니다.
    """
    __tablename__ = "image_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "image_post_id", name="uq_user_image_like"),
    )
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 좋아요 누른 사용자
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # 좋아요 대상 이미지
    image_post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("image_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 관계
    image_post: Mapped["ImagePost"] = relationship(
        "ImagePost",
        back_populates="likes"
    )
    
    def __repr__(self) -> str:
        return f"<ImageLike(user_id={self.user_id}, image_post_id={self.image_post_id})>"
```

### TournamentVote 모델

```python
# app/models/tournament_vote.py
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.image_post import ImagePost

class TournamentVote(Base, TimestampMixin):
    """
    토너먼트 투표 모델
    
    두 이미지 중 하나를 선택하는 투표 기록을 저장합니다.
    동일한 이미지가 승자와 패자가 될 수 없습니다.
    match_id를 통해 매치 단위 중복 투표 방지 및 통계 관리가 가능합니다.
    """
    __tablename__ = "tournament_votes"
    __table_args__ = (
        CheckConstraint(
            "winner_image_id <> loser_image_id",
            name="ck_different_images"
        ),
        Index("ix_tournament_votes_match_id", "match_id"),
        Index("ix_tournament_votes_voter_match", "voter_id", "match_id"),
    )
    
    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 매치 식별자 (UUID) - 부정 투표 방지 및 매치 단위 통계용
    match_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="매치 고유 식별자 (UUID)"
    )
    
    # 투표한 사용자
    voter_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # 승리 이미지
    winner_image_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("image_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 패배 이미지
    loser_image_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("image_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 관계
    winner_image: Mapped["ImagePost"] = relationship(
        "ImagePost",
        foreign_keys=[winner_image_id],
        back_populates="won_tournaments"
    )
    
    loser_image: Mapped["ImagePost"] = relationship(
        "ImagePost",
        foreign_keys=[loser_image_id],
        back_populates="lost_tournaments"
    )
    
    def __repr__(self) -> str:
        return f"<TournamentVote(match={self.match_id}, winner={self.winner_image_id}, loser={self.loser_image_id})>"


# 매치 생성 헬퍼 함수
def generate_match_id() -> str:
    """새로운 매치 ID 생성"""
    return str(uuid.uuid4())
```

#### match_id 활용 예시

```python
# 매치 생성 시
match_id = generate_match_id()
# Redis나 캐시에 매치 정보 저장 (유효시간 5분)
await cache.set(f"match:{match_id}", {
    "image_ids": [15, 28],
    "created_at": datetime.utcnow().isoformat()
}, expire=300)

# 투표 시 검증
async def validate_match(match_id: str, winner_id: int, loser_id: int) -> bool:
    """매치 유효성 검증"""
    match_data = await cache.get(f"match:{match_id}")
    if not match_data:
        return False  # 만료된 매치
    
    # 이미지 ID가 매치에 포함되어 있는지 확인
    valid_ids = set(match_data["image_ids"])
    return {winner_id, loser_id} == valid_ids

# 중복 투표 방지
async def check_duplicate_vote(db: AsyncSession, voter_id: int, match_id: str) -> bool:
    """같은 매치에 이미 투표했는지 확인"""
    stmt = select(TournamentVote).where(
        TournamentVote.voter_id == voter_id,
        TournamentVote.match_id == match_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
```

---

## 📝 모델 초기화

```python
# app/models/__init__.py
from app.models.base import Base
from app.models.image_post import ImagePost
from app.models.image_like import ImageLike
from app.models.tournament_vote import TournamentVote

__all__ = [
    "Base",
    "ImagePost",
    "ImageLike",
    "TournamentVote",
]
```

---

## 🔧 테이블 생성 스크립트

개발 환경에서 테이블을 생성하는 스크립트입니다.

```python
# scripts/create_tables.py
import asyncio
from app.core.database import engine
from app.models import Base

async def create_tables():
    """모든 테이블을 생성합니다."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 모든 테이블이 생성되었습니다.")

if __name__ == "__main__":
    asyncio.run(create_tables())
```

---

## 📊 랭킹 계산 쿼리

### 최근 24시간 인기 Top 10

```python
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

async def get_top_images_24h(db: AsyncSession, limit: int = 10):
    """
    최근 24시간 기준 좋아요 + 토너먼트 승수 합산 Top N 이미지
    """
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    # 서브쿼리: 최근 24시간 좋아요 수
    like_subq = (
        select(
            ImageLike.image_post_id,
            func.count(ImageLike.id).label("like_count")
        )
        .where(ImageLike.created_at >= cutoff)
        .group_by(ImageLike.image_post_id)
        .subquery()
    )
    
    # 서브쿼리: 최근 24시간 토너먼트 승수
    win_subq = (
        select(
            TournamentVote.winner_image_id,
            func.count(TournamentVote.id).label("win_count")
        )
        .where(TournamentVote.created_at >= cutoff)
        .group_by(TournamentVote.winner_image_id)
        .subquery()
    )
    
    # 메인 쿼리: 합산 점수로 정렬
    stmt = (
        select(
            ImagePost,
            func.coalesce(like_subq.c.like_count, 0).label("like_count"),
            func.coalesce(win_subq.c.win_count, 0).label("win_count"),
            (
                func.coalesce(like_subq.c.like_count, 0) +
                func.coalesce(win_subq.c.win_count, 0)
            ).label("total_score")
        )
        .outerjoin(like_subq, ImagePost.id == like_subq.c.image_post_id)
        .outerjoin(win_subq, ImagePost.id == win_subq.c.winner_image_id)
        .where(ImagePost.is_active == True)
        .order_by(desc("total_score"))
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    return result.all()
```