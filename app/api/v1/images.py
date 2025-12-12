"""
이미지 API 라우터

이미지 CRUD 엔드포인트를 제공합니다.
"""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.image import ImageResponse, ImageListResponse, ImageUpdateRequest
from app.services.image_service import ImageService
from app.utils.file_handler import validate_and_save_file, delete_file

router = APIRouter(prefix="/images", tags=["Images"])


@router.post(
    "/",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI 이미지 업로드",
    description="""
    AI로 생성한 이미지를 업로드합니다.

    ## 최종 경로
    `POST /api-image/v1/images/`

    ## 요청 조건
    - **인증 필수**: JWT 토큰이 Authorization 헤더에 포함되어야 합니다
    - **파일 제한**: 최대 10MB, jpg/jpeg/png/gif/webp 형식만 허용

    ## 응답
    - **201**: 업로드 성공, 생성된 이미지 정보 반환
    - **400**: 잘못된 파일 형식 또는 크기 초과
    - **401**: 인증 실패
    """,
)
async def create_image(
    file: UploadFile = File(..., description="업로드할 이미지 파일"),
    prompt: str = Form(..., description="AI 생성 프롬프트", min_length=1, max_length=2000),
    model_name: Optional[str] = Form(None, description="사용한 AI 모델명", max_length=100),
    is_tournament_opt_in: bool = Form(False, description="토너먼트 참여 여부"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """AI 이미지를 업로드하고 메타데이터를 저장합니다."""

    # 1. 파일 검증 및 저장
    image_url = await validate_and_save_file(file)

    # 2. 데이터베이스에 저장
    try:
        image = await ImageService.create_image(
            db=db,
            user_id=current_user["user_id"],
            image_url=image_url,
            prompt=prompt,
            model_name=model_name,
            is_tournament_opt_in=is_tournament_opt_in
        )

        return ImageResponse(
            **image.__dict__,
            like_count=0
        )

    except Exception as e:
        # DB 저장 실패 시 업로드된 파일 삭제
        await delete_file(image_url)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이미지 저장 중 오류가 발생했습니다: {str(e)}"
        )


@router.get(
    "/",
    response_model=ImageListResponse,
    summary="이미지 목록 조회",
    description="""
    이미지 목록을 조회합니다.

    ## 최종 경로
    `GET /api-image/v1/images/`

    ## 쿼리 파라미터
    - page: 페이지 번호 (기본값: 1)
    - size: 페이지 크기 (기본값: 20)
    - user_id: 특정 사용자의 이미지만 조회 (선택사항)
    - tournament_only: 토너먼트 참여 이미지만 조회 (선택사항)
    """,
)
async def get_images(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    user_id: Optional[int] = Query(None, description="사용자 ID 필터"),
    tournament_only: bool = Query(False, description="토너먼트 참여 이미지만 조회"),
    db: AsyncSession = Depends(get_db)
):
    """이미지 목록을 페이지네이션하여 반환합니다."""
    return await ImageService.get_images(
        db=db,
        page=page,
        size=size,
        user_id=user_id,
        tournament_only=tournament_only
    )


@router.get(
    "/{image_id}",
    response_model=ImageResponse,
    summary="이미지 상세 조회",
    description="""
    특정 이미지의 상세 정보를 조회합니다.

    ## 최종 경로
    `GET /api-image/v1/images/{image_id}`
    """,
)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """ID로 이미지 상세 정보를 조회합니다."""
    image = await ImageService.get_image_by_id(db, image_id)

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="이미지를 찾을 수 없습니다."
        )

    return ImageResponse(
        **image.__dict__,
        like_count=image.like_count
    )


@router.put(
    "/{image_id}",
    response_model=ImageResponse,
    summary="이미지 수정",
    description="""
    이미지 메타데이터를 수정합니다.

    ## 최종 경로
    `PUT /api-image/v1/images/{image_id}`

    ## 요청 조건
    - **인증 필수**: 자신의 이미지만 수정 가능
    """,
)
async def update_image(
    image_id: int,
    data: ImageUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """이미지 메타데이터를 수정합니다."""
    image = await ImageService.update_image(
        db=db,
        image_id=image_id,
        user_id=current_user["user_id"],
        prompt=data.prompt,
        model_name=data.model_name,
        is_tournament_opt_in=data.is_tournament_opt_in
    )

    return ImageResponse(
        **image.__dict__,
        like_count=image.like_count
    )


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="이미지 삭제",
    description="""
    이미지를 삭제합니다 (Soft Delete).

    ## 최종 경로
    `DELETE /api-image/v1/images/{image_id}`

    ## 요청 조건
    - **인증 필수**: 자신의 이미지만 삭제 가능
    """,
)
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """이미지를 삭제합니다 (is_active = False)."""
    await ImageService.delete_image(
        db=db,
        image_id=image_id,
        user_id=current_user["user_id"]
    )

    return None


@router.get(
    "/feed/random",
    response_model=list[ImageResponse],
    summary="랜덤 피드",
    description="""
    랜덤하게 이미지를 조회합니다.

    ## 최종 경로
    `GET /api-image/v1/images/feed/random`

    ## 쿼리 파라미터
    - limit: 조회할 이미지 개수 (기본값: 20, 최대: 50)

    ## 인증
    - 인증 불필요 (누구나 조회 가능)
    """,
)
async def get_random_feed(
    limit: int = Query(20, ge=1, le=50, description="조회할 이미지 개수"),
    db: AsyncSession = Depends(get_db)
):
    """랜덤 피드를 조회합니다."""
    images = await ImageService.get_random_feed(db=db, limit=limit)

    return [
        ImageResponse(**image.__dict__, like_count=image.like_count)
        for image in images
    ]


@router.get(
    "/feed/top-24h",
    response_model=list[ImageResponse],
    summary="인기 Top 이미지 (24시간)",
    description="""
    최근 24시간 내 좋아요가 많은 이미지를 조회합니다.

    ## 최종 경로
    `GET /api-image/v1/images/feed/top-24h`

    ## 쿼리 파라미터
    - limit: 조회할 이미지 개수 (기본값: 10, 최대: 50)

    ## 인증
    - 인증 불필요 (누구나 조회 가능)
    """,
)
async def get_top_images_24h(
    limit: int = Query(10, ge=1, le=50, description="조회할 이미지 개수"),
    db: AsyncSession = Depends(get_db)
):
    """최근 24시간 내 인기 이미지를 조회합니다."""
    images = await ImageService.get_top_images_24h(db=db, limit=limit)

    return [
        ImageResponse(**image.__dict__, like_count=image.like_count)
        for image in images
    ]
