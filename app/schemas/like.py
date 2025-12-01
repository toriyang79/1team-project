"""
좋아요 Pydantic 스키마

좋아요 요청/응답 스키마를 정의합니다.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LikeResponse(BaseModel):
    """좋아요 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_post_id: int
    created_at: datetime


class LikeStatusResponse(BaseModel):
    """좋아요 상태 응답 스키마"""
    is_liked: bool
    like_count: int
    message: str
