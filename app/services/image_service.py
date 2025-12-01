"""
이미지 서비스 레이어

이미지 관련 비즈니스 로직을 처리합니다.
"""

from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.image_post import ImagePost
from app.schemas.image import ImageResponse, ImageListResponse


class ImageService:
    """이미지 관련 비즈니스 로직을 처리하는 서비스 클래스"""

    @staticmethod
    async def create_image(
        db: AsyncSession,
        user_id: int,
        image_url: str,
        prompt: str,
        model_name: Optional[str] = None,
        is_tournament_opt_in: bool = False
    ) -> ImagePost:
        """
        새로운 이미지 게시물을 생성합니다.

        Args:
            db: 데이터베이스 세션
            user_id: 작성자 ID
            image_url: 이미지 URL
            prompt: AI 생성 프롬프트
            model_name: 사용한 AI 모델명
            is_tournament_opt_in: 토너먼트 참여 여부

        Returns:
            ImagePost: 생성된 이미지 게시물
        """
        new_image = ImagePost(
            user_id=user_id,
            image_url=image_url,
            prompt=prompt,
            model_name=model_name,
            is_tournament_opt_in=is_tournament_opt_in,
        )

        db.add(new_image)
        await db.flush()
        await db.refresh(new_image)

        return new_image

    @staticmethod
    async def get_image_by_id(
        db: AsyncSession,
        image_id: int,
        include_inactive: bool = False
    ) -> Optional[ImagePost]:
        """
        ID로 이미지를 조회합니다.

        Args:
            db: 데이터베이스 세션
            image_id: 이미지 ID
            include_inactive: 비활성 이미지 포함 여부

        Returns:
            Optional[ImagePost]: 이미지 게시물 또는 None
        """
        stmt = select(ImagePost).where(ImagePost.id == image_id)

        if not include_inactive:
            stmt = stmt.where(ImagePost.is_active == True)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_images(
        db: AsyncSession,
        page: int = 1,
        size: int = 20,
        user_id: Optional[int] = None,
        tournament_only: bool = False
    ) -> ImageListResponse:
        """
        이미지 목록을 조회합니다.

        Args:
            db: 데이터베이스 세션
            page: 페이지 번호 (1부터 시작)
            size: 페이지 크기
            user_id: 특정 사용자의 이미지만 조회
            tournament_only: 토너먼트 참여 이미지만 조회

        Returns:
            ImageListResponse: 이미지 목록 응답
        """
        # 기본 쿼리
        stmt = select(ImagePost).where(ImagePost.is_active == True)

        # 필터 적용
        if user_id:
            stmt = stmt.where(ImagePost.user_id == user_id)

        if tournament_only:
            stmt = stmt.where(ImagePost.is_tournament_opt_in == True)

        # 전체 개수 조회
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # 페이지네이션
        offset = (page - 1) * size
        stmt = stmt.order_by(ImagePost.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(stmt)
        images = result.scalars().all()

        # 응답 생성
        items = [
            ImageResponse(
                **image.__dict__,
                like_count=image.like_count
            )
            for image in images
        ]

        return ImageListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            has_next=(offset + size) < total
        )

    @staticmethod
    async def update_image(
        db: AsyncSession,
        image_id: int,
        user_id: int,
        prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        is_tournament_opt_in: Optional[bool] = None
    ) -> ImagePost:
        """
        이미지 게시물을 수정합니다.

        Args:
            db: 데이터베이스 세션
            image_id: 이미지 ID
            user_id: 요청 사용자 ID (권한 확인용)
            prompt: 수정할 프롬프트
            model_name: 수정할 모델명
            is_tournament_opt_in: 수정할 토너먼트 참여 여부

        Returns:
            ImagePost: 수정된 이미지 게시물

        Raises:
            HTTPException: 이미지를 찾을 수 없거나 권한이 없는 경우
        """
        image = await ImageService.get_image_by_id(db, image_id)

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이미지를 찾을 수 없습니다."
            )

        # 권한 확인
        if image.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이미지를 수정할 권한이 없습니다."
            )

        # 필드 업데이트
        if prompt is not None:
            image.prompt = prompt
        if model_name is not None:
            image.model_name = model_name
        if is_tournament_opt_in is not None:
            image.is_tournament_opt_in = is_tournament_opt_in

        await db.flush()
        await db.refresh(image)

        return image

    @staticmethod
    async def delete_image(
        db: AsyncSession,
        image_id: int,
        user_id: int
    ) -> bool:
        """
        이미지 게시물을 삭제합니다 (Soft Delete).

        Args:
            db: 데이터베이스 세션
            image_id: 이미지 ID
            user_id: 요청 사용자 ID (권한 확인용)

        Returns:
            bool: 삭제 성공 여부

        Raises:
            HTTPException: 이미지를 찾을 수 없거나 권한이 없는 경우
        """
        image = await ImageService.get_image_by_id(db, image_id)

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이미지를 찾을 수 없습니다."
            )

        # 권한 확인
        if image.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이미지를 삭제할 권한이 없습니다."
            )

        # Soft Delete
        image.is_active = False
        await db.flush()

        return True

    @staticmethod
    async def get_random_feed(
        db: AsyncSession,
        limit: int = 20
    ) -> list[ImagePost]:
        """
        랜덤 피드를 조회합니다.

        Args:
            db: 데이터베이스 세션
            limit: 조회할 이미지 개수

        Returns:
            list[ImagePost]: 랜덤 이미지 목록
        """
        from sqlalchemy import func as sql_func

        # 랜덤 정렬로 이미지 조회
        stmt = (
            select(ImagePost)
            .where(ImagePost.is_active == True)
            .order_by(sql_func.random())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_top_images_24h(
        db: AsyncSession,
        limit: int = 10
    ) -> list[ImagePost]:
        """
        최근 24시간 내 좋아요가 많은 이미지 Top N을 조회합니다.

        Args:
            db: 데이터베이스 세션
            limit: 조회할 이미지 개수

        Returns:
            list[ImagePost]: 인기 이미지 목록
        """
        from datetime import datetime, timedelta
        from sqlalchemy import func as sql_func
        from app.models.image_like import ImageLike

        # 24시간 전 시간
        time_24h_ago = datetime.utcnow() - timedelta(hours=24)

        # 최근 24시간 내 좋아요 수를 집계하여 정렬
        stmt = (
            select(ImagePost)
            .outerjoin(ImageLike, ImagePost.id == ImageLike.image_post_id)
            .where(
                and_(
                    ImagePost.is_active == True,
                    ImagePost.created_at >= time_24h_ago
                )
            )
            .group_by(ImagePost.id)
            .order_by(sql_func.count(ImageLike.id).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()
