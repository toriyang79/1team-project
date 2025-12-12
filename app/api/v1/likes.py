"""
좋아요 API 라우터

좋아요 추가/취소 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.like import LikeResponse, LikeStatusResponse
from app.services.like_service import LikeService

router = APIRouter(prefix="/images", tags=["Likes"])


@router.post(
    "/{image_id}/like",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="좋아요 추가",
    description="""
    이미지에 좋아요를 추가합니다.

    ## 최종 경로
    `POST /api-image/v1/images/{image_id}/like`

    ## 요청 조건
    - **인증 필수**: JWT 토큰이 Authorization 헤더에 포함되어야 합니다
    - 이미 좋아요를 눌렀다면 400 에러 반환

    ## 응답
    - **201**: 좋아요 추가 성공
    - **400**: 이미 좋아요를 눌렀음
    - **404**: 이미지를 찾을 수 없음
    - **401**: 인증 실패
    """,
)
async def add_like(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """이미지에 좋아요를 추가합니다."""
    await LikeService.add_like(
        db=db,
        user_id=current_user["user_id"],
        image_post_id=image_id
    )

    # 현재 좋아요 개수 조회
    like_count = await LikeService.get_like_count(db=db, image_post_id=image_id)

    return LikeStatusResponse(
        is_liked=True,
        like_count=like_count,
        message="좋아요를 추가했습니다."
    )


@router.delete(
    "/{image_id}/like",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="좋아요 취소",
    description="""
    이미지의 좋아요를 취소합니다.

    ## 최종 경로
    `DELETE /api-image/v1/images/{image_id}/like`

    ## 요청 조건
    - **인증 필수**: JWT 토큰이 Authorization 헤더에 포함되어야 합니다
    - 좋아요를 누르지 않았다면 404 에러 반환

    ## 응답
    - **200**: 좋아요 취소 성공
    - **404**: 좋아요를 찾을 수 없음
    - **401**: 인증 실패
    """,
)
async def remove_like(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """이미지의 좋아요를 취소합니다."""
    await LikeService.remove_like(
        db=db,
        user_id=current_user["user_id"],
        image_post_id=image_id
    )

    # 현재 좋아요 개수 조회
    like_count = await LikeService.get_like_count(db=db, image_post_id=image_id)

    return LikeStatusResponse(
        is_liked=False,
        like_count=like_count,
        message="좋아요를 취소했습니다."
    )


@router.get(
    "/{image_id}/like/status",
    response_model=LikeStatusResponse,
    summary="좋아요 상태 조회",
    description="""
    사용자가 해당 이미지에 좋아요를 눌렀는지 확인합니다.

    ## 최종 경로
    `GET /api-image/v1/images/{image_id}/like/status`

    ## 요청 조건
    - **인증 필수**: JWT 토큰이 Authorization 헤더에 포함되어야 합니다

    ## 응답
    - **200**: 좋아요 상태 반환
    - **401**: 인증 실패
    """,
)
async def get_like_status(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """사용자의 좋아요 상태를 조회합니다."""
    is_liked = await LikeService.check_like_status(
        db=db,
        user_id=current_user["user_id"],
        image_post_id=image_id
    )

    like_count = await LikeService.get_like_count(db=db, image_post_id=image_id)

    return LikeStatusResponse(
        is_liked=is_liked,
        like_count=like_count,
        message="좋아요 상태를 조회했습니다."
    )
