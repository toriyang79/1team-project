"""
좋아요 서비스 레이어

좋아요 관련 비즈니스 로직을 처리합니다.
"""

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.image_like import ImageLike
from app.models.image_post import ImagePost


class LikeService:
    """좋아요 관련 비즈니스 로직을 처리하는 서비스 클래스"""

    @staticmethod
    async def add_like(
        db: AsyncSession,
        user_id: int,
        image_post_id: int
    ) -> ImageLike:
        """
        이미지에 좋아요를 추가합니다.

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            image_post_id: 이미지 게시물 ID

        Returns:
            ImageLike: 생성된 좋아요

        Raises:
            HTTPException: 이미지가 존재하지 않거나 이미 좋아요를 눌렀을 경우
        """
        # 이미지 존재 확인
        stmt = select(ImagePost).where(
            and_(
                ImagePost.id == image_post_id,
                ImagePost.is_active == True
            )
        )
        result = await db.execute(stmt)
        image = result.scalar_one_or_none()

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이미지를 찾을 수 없습니다."
            )

        # 좋아요 생성
        new_like = ImageLike(
            user_id=user_id,
            image_post_id=image_post_id
        )

        db.add(new_like)

        try:
            await db.flush()
            await db.refresh(new_like)
            return new_like

        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 좋아요를 눌렀습니다."
            )

    @staticmethod
    async def remove_like(
        db: AsyncSession,
        user_id: int,
        image_post_id: int
    ) -> bool:
        """
        이미지의 좋아요를 취소합니다.

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            image_post_id: 이미지 게시물 ID

        Returns:
            bool: 삭제 성공 여부

        Raises:
            HTTPException: 좋아요를 찾을 수 없는 경우
        """
        # 좋아요 조회
        stmt = select(ImageLike).where(
            and_(
                ImageLike.user_id == user_id,
                ImageLike.image_post_id == image_post_id
            )
        )
        result = await db.execute(stmt)
        like = result.scalar_one_or_none()

        if not like:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="좋아요를 찾을 수 없습니다."
            )

        # 좋아요 삭제
        await db.delete(like)
        await db.flush()

        return True

    @staticmethod
    async def check_like_status(
        db: AsyncSession,
        user_id: int,
        image_post_id: int
    ) -> bool:
        """
        사용자가 해당 이미지에 좋아요를 눌렀는지 확인합니다.

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            image_post_id: 이미지 게시물 ID

        Returns:
            bool: 좋아요 여부
        """
        stmt = select(ImageLike).where(
            and_(
                ImageLike.user_id == user_id,
                ImageLike.image_post_id == image_post_id
            )
        )
        result = await db.execute(stmt)
        like = result.scalar_one_or_none()

        return like is not None

    @staticmethod
    async def get_like_count(
        db: AsyncSession,
        image_post_id: int
    ) -> int:
        """
        이미지의 좋아요 개수를 조회합니다.

        Args:
            db: 데이터베이스 세션
            image_post_id: 이미지 게시물 ID

        Returns:
            int: 좋아요 개수
        """
        from sqlalchemy import func

        stmt = select(func.count(ImageLike.id)).where(
            ImageLike.image_post_id == image_post_id
        )
        result = await db.execute(stmt)
        count = result.scalar_one()

        return count
