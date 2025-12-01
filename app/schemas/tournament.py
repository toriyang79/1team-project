"""
토너먼트 Pydantic 스키마

토너먼트 요청/응답 스키마를 정의합니다.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.image import ImageResponse


class TournamentMatchResponse(BaseModel):
    """토너먼트 매칭 응답 스키마"""
    image1: ImageResponse
    image2: ImageResponse
    message: str = "두 이미지 중 마음에 드는 것을 선택하세요!"


class TournamentVoteRequest(BaseModel):
    """토너먼트 투표 요청 스키마"""
    winner_image_id: int
    loser_image_id: int


class TournamentVoteResponse(BaseModel):
    """토너먼트 투표 응답 스키마"""
    vote_id: int
    winner_image_id: int
    loser_image_id: int
    winner_new_win_count: int
    message: str


class TournamentRankingItem(BaseModel):
    """토너먼트 랭킹 아이템"""
    model_config = ConfigDict(from_attributes=True)

    rank: int
    image: ImageResponse
    win_count: int


class TournamentRankingResponse(BaseModel):
    """토너먼트 랭킹 응답"""
    rankings: list[TournamentRankingItem]
    total: int
