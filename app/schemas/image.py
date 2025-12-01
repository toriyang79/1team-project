"""
이미지 게시물 Pydantic 스키마

요청/응답 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ===== 요청 스키마 =====
class ImageCreateRequest(BaseModel):
    """이미지 업로드 요청 스키마 (multipart/form-data 사용)"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="AI 생성 프롬프트")
    model_name: Optional[str] = Field(None, max_length=100, description="사용한 AI 모델명")
    is_tournament_opt_in: bool = Field(False, description="토너먼트 참여 여부")


class ImageUpdateRequest(BaseModel):
    """이미지 수정 요청 스키마"""
    prompt: Optional[str] = Field(None, min_length=1, max_length=2000)
    model_name: Optional[str] = Field(None, max_length=100)
    is_tournament_opt_in: Optional[bool] = None


# ===== 응답 스키마 =====
class ImageResponse(BaseModel):
    """이미지 단일 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_url: str
    prompt: str
    model_name: Optional[str]
    is_tournament_opt_in: bool
    tournament_win_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    like_count: int = 0


class ImageListResponse(BaseModel):
    """이미지 목록 응답 스키마"""
    items: list[ImageResponse]
    total: int
    page: int
    size: int
    has_next: bool


class ImageDetailResponse(ImageResponse):
    """이미지 상세 응답 스키마 (추가 정보 포함 가능)"""
    pass
