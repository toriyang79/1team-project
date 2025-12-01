"""
토너먼트 서비스 레이어

토너먼트 관련 비즈니스 로직을 처리합니다.
"""

from typing import Tuple, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.image_post import ImagePost
from app.models.tournament_vote import TournamentVote


class TournamentService:
    """토너먼트 관련 비즈니스 로직을 처리하는 서비스 클래스"""

    @staticmethod
    async def get_random_match(
        db: AsyncSession
    ) -> Tuple[ImagePost, ImagePost]:
        """
        토너먼트를 위한 랜덤 이미지 2개를 매칭합니다.

        Args:
            db: 데이터베이스 세션

        Returns:
            Tuple[ImagePost, ImagePost]: 랜덤으로 선택된 2개의 이미지

        Raises:
            HTTPException: 토너먼트 참여 이미지가 2개 미만인 경우
        """
        # 토너먼트 참여 이미지 중 랜덤으로 2개 선택
        stmt = (
            select(ImagePost)
            .where(
                and_(
                    ImagePost.is_active == True,
                    ImagePost.is_tournament_opt_in == True
                )
            )
            .order_by(func.random())
            .limit(2)
        )

        result = await db.execute(stmt)
        images = result.scalars().all()

        if len(images) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="토너먼트 참여 이미지가 부족합니다. 최소 2개 이상 필요합니다."
            )

        return images[0], images[1]

    @staticmethod
    async def record_vote(
        db: AsyncSession,
        user_id: int,
        winner_image_id: int,
        loser_image_id: int
    ) -> Tuple[TournamentVote, int]:
        """
        토너먼트 투표를 기록하고 승자의 승리 횟수를 증가시킵니다.

        Args:
            db: 데이터베이스 세션
            user_id: 투표한 사용자 ID
            winner_image_id: 승리한 이미지 ID
            loser_image_id: 패배한 이미지 ID

        Returns:
            Tuple[TournamentVote, int]: (투표 기록, 승자의 새로운 승리 횟수)

        Raises:
            HTTPException: 이미지를 찾을 수 없거나 동일한 이미지를 선택한 경우
        """
        # 같은 이미지를 선택했는지 확인
        if winner_image_id == loser_image_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="동일한 이미지를 선택할 수 없습니다."
            )

        # 승자 이미지 확인 및 승리 횟수 증가
        winner_stmt = select(ImagePost).where(
            and_(
                ImagePost.id == winner_image_id,
                ImagePost.is_active == True,
                ImagePost.is_tournament_opt_in == True
            )
        )
        winner_result = await db.execute(winner_stmt)
        winner_image = winner_result.scalar_one_or_none()

        if not winner_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="승자 이미지를 찾을 수 없거나 토너먼트에 참여하지 않은 이미지입니다."
            )

        # 패자 이미지 확인
        loser_stmt = select(ImagePost).where(
            and_(
                ImagePost.id == loser_image_id,
                ImagePost.is_active == True,
                ImagePost.is_tournament_opt_in == True
            )
        )
        loser_result = await db.execute(loser_stmt)
        loser_image = loser_result.scalar_one_or_none()

        if not loser_image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="패자 이미지를 찾을 수 없거나 토너먼트에 참여하지 않은 이미지입니다."
            )

        # 승자의 승리 횟수 증가
        winner_image.tournament_win_count += 1
        await db.flush()

        # 투표 기록 생성
        vote = TournamentVote(
            user_id=user_id,
            winner_image_id=winner_image_id,
            loser_image_id=loser_image_id
        )
        db.add(vote)
        await db.flush()
        await db.refresh(vote)

        return vote, winner_image.tournament_win_count

    @staticmethod
    async def get_rankings(
        db: AsyncSession,
        limit: int = 50
    ) -> list[ImagePost]:
        """
        토너먼트 랭킹을 조회합니다.

        Args:
            db: 데이터베이스 세션
            limit: 조회할 랭킹 개수

        Returns:
            list[ImagePost]: 승리 횟수 기준 정렬된 이미지 목록
        """
        stmt = (
            select(ImagePost)
            .where(
                and_(
                    ImagePost.is_active == True,
                    ImagePost.is_tournament_opt_in == True
                )
            )
            .order_by(ImagePost.tournament_win_count.desc(), ImagePost.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()
