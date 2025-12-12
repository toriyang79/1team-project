"""
토너먼트 API 라우터

토너먼트 매칭, 투표, 랭킹 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.tournament import (
    TournamentMatchResponse,
    TournamentVoteRequest,
    TournamentVoteResponse,
    TournamentRankingResponse,
    TournamentRankingItem
)
from app.schemas.image import ImageResponse
from app.services.tournament_service import TournamentService

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


@router.get(
    "/match",
    response_model=TournamentMatchResponse,
    summary="토너먼트 랜덤 매칭",
    description="""
    토너먼트를 위한 랜덤 이미지 2개를 매칭합니다.

    ## 최종 경로
    `GET /api-image/v1/tournaments/match`

    ## 조건
    - is_tournament_opt_in=true인 이미지만 선택됩니다
    - 최소 2개 이상의 토너먼트 참여 이미지가 필요합니다

    ## 인증
    - 인증 불필요 (누구나 조회 가능)

    ## 응답
    - **200**: 2개의 이미지 매칭 성공
    - **400**: 토너먼트 참여 이미지가 2개 미만
    """,
)
async def get_tournament_match(
    db: AsyncSession = Depends(get_db)
):
    """토너먼트를 위한 랜덤 이미지 2개를 반환합니다."""
    image1, image2 = await TournamentService.get_random_match(db=db)

    return TournamentMatchResponse(
        image1=ImageResponse(**image1.__dict__, like_count=image1.like_count),
        image2=ImageResponse(**image2.__dict__, like_count=image2.like_count),
        message="두 이미지 중 마음에 드는 것을 선택하세요!"
    )


@router.post(
    "/vote",
    response_model=TournamentVoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="토너먼트 투표",
    description="""
    토너먼트에서 승자를 선택하여 투표합니다.

    ## 최종 경로
    `POST /api-image/v1/tournaments/vote`

    ## 요청 조건
    - **인증 필수**: JWT 토큰이 Authorization 헤더에 포함되어야 합니다
    - winner_image_id와 loser_image_id가 다른 값이어야 합니다
    - 두 이미지 모두 토너먼트에 참여해야 합니다

    ## 효과
    - 승자의 tournament_win_count가 1 증가합니다
    - 투표 기록이 tournament_votes 테이블에 저장됩니다

    ## 응답
    - **201**: 투표 성공
    - **400**: 동일한 이미지 선택 또는 유효하지 않은 이미지
    - **404**: 이미지를 찾을 수 없음
    - **401**: 인증 실패
    """,
)
async def vote_tournament(
    vote_data: TournamentVoteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """토너먼트 투표를 기록하고 승자의 승리 횟수를 증가시킵니다."""
    vote, new_win_count = await TournamentService.record_vote(
        db=db,
        user_id=current_user["user_id"],
        winner_image_id=vote_data.winner_image_id,
        loser_image_id=vote_data.loser_image_id
    )

    return TournamentVoteResponse(
        vote_id=vote.id,
        winner_image_id=vote.winner_image_id,
        loser_image_id=vote.loser_image_id,
        winner_new_win_count=new_win_count,
        message="투표가 완료되었습니다!"
    )


@router.get(
    "/rankings",
    response_model=TournamentRankingResponse,
    summary="토너먼트 랭킹",
    description="""
    토너먼트 승리 횟수 기준 랭킹을 조회합니다.

    ## 최종 경로
    `GET /api-image/v1/tournaments/rankings`

    ## 쿼리 파라미터
    - limit: 조회할 랭킹 개수 (기본값: 50, 최대: 100)

    ## 정렬 기준
    1. tournament_win_count (내림차순)
    2. created_at (내림차순) - 승리 횟수가 같을 경우

    ## 인증
    - 인증 불필요 (누구나 조회 가능)
    """,
)
async def get_tournament_rankings(
    limit: int = Query(50, ge=1, le=100, description="조회할 랭킹 개수"),
    db: AsyncSession = Depends(get_db)
):
    """토너먼트 랭킹을 조회합니다."""
    images = await TournamentService.get_rankings(db=db, limit=limit)

    rankings = [
        TournamentRankingItem(
            rank=idx + 1,
            image=ImageResponse(**image.__dict__, like_count=image.like_count),
            win_count=image.tournament_win_count
        )
        for idx, image in enumerate(images)
    ]

    return TournamentRankingResponse(
        rankings=rankings,
        total=len(rankings)
    )
