"""
JWT 토큰 생성 테스트 엔드포인트

⚠️ 개발 환경 전용 엔드포인트입니다!
운영 환경에서는 이 파일을 삭제하거나 비활성화해야 합니다.

Django Auth 서버와 연동 시 이 엔드포인트는 제거됩니다.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from jose import jwt

from app.core.config import settings

router = APIRouter(prefix="/auth-test", tags=["Auth Test (개발 전용)"])


class TokenRequest(BaseModel):
    """토큰 생성 요청"""
    user_id: int
    expires_minutes: int = 60  # 기본 1시간


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user_id: int


@router.post(
    "/generate-token",
    response_model=TokenResponse,
    summary="테스트용 JWT 토큰 생성",
    description="""
    ⚠️ **개발 환경 전용 엔드포인트입니다!**

    테스트용 JWT 토큰을 생성합니다.

    ## 사용 방법
    1. 이 엔드포인트로 토큰을 생성합니다
    2. 생성된 `access_token`을 복사합니다
    3. Swagger UI 상단의 🔓 Authorize 버튼을 클릭합니다
    4. "Bearer {생성된 토큰}"을 입력합니다 (Bearer 접두사 포함)
    5. 이제 인증이 필요한 엔드포인트를 테스트할 수 있습니다

    ## 주의사항
    - 운영 환경에서는 Django Auth 서버가 토큰을 발급합니다
    - 이 엔드포인트는 Django 연동 시 제거됩니다
    """,
)
async def generate_test_token(data: TokenRequest):
    """개발용 JWT 토큰을 생성합니다."""

    if not settings.JWT_PRIVATE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_PRIVATE_KEY가 설정되지 않았습니다. .env 파일을 확인하세요."
        )

    # 토큰 만료 시간
    expires_at = datetime.utcnow() + timedelta(minutes=data.expires_minutes)

    # JWT 페이로드
    payload = {
        "user_id": data.user_id,
        "exp": expires_at,
        "iat": datetime.utcnow(),
    }

    # 토큰 생성
    try:
        token = jwt.encode(
            payload,
            settings.JWT_PRIVATE_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        return TokenResponse(
            access_token=token,
            expires_at=expires_at,
            user_id=data.user_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토큰 생성 실패: {str(e)}"
        )
