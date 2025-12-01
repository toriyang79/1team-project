"""
JWT 인증 및 보안 관련 기능

Django Auth 서버에서 발급한 JWT 토큰을 검증합니다.
RS256 알고리즘(비대칭키)을 사용하여 Public Key로 서명을 검증합니다.
"""

from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.core.config import settings

# ===== HTTP Bearer 인증 스키마 =====
security = HTTPBearer()


async def verify_jwt_token(token: str) -> Dict:
    """
    JWT 토큰을 검증하고 페이로드를 반환합니다.

    Args:
        token: JWT 토큰 문자열

    Returns:
        Dict: 검증된 페이로드

    Raises:
        HTTPException: 토큰이 유효하지 않을 경우
    """
    try:
        # RS256 알고리즘으로 토큰 검증
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    현재 인증된 사용자 정보를 반환하는 의존성 함수입니다.

    Authorization 헤더에서 JWT 토큰을 추출하고 검증합니다.

    Args:
        credentials: HTTP Bearer 인증 정보

    Returns:
        Dict: 사용자 정보
            - user_id: 사용자 ID
            - payload: 전체 JWT 페이로드

    Raises:
        HTTPException: 토큰이 없거나 유효하지 않을 경우

    Example:
        ```python
        @router.get("/me")
        async def get_me(current_user: Dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
            return {"user_id": user_id}
        ```
    """
    token = credentials.credentials

    # 토큰 검증
    payload = await verify_jwt_token(token)

    # user_id 추출
    user_id: Optional[int] = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: user_id not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "payload": payload,
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict]:
    """
    선택적으로 사용자 정보를 반환하는 의존성 함수입니다.

    토큰이 없어도 에러가 발생하지 않습니다.
    인증된 사용자와 비인증 사용자 모두 접근 가능한 엔드포인트에서 사용합니다.

    Args:
        credentials: HTTP Bearer 인증 정보 (선택사항)

    Returns:
        Optional[Dict]: 사용자 정보 또는 None

    Example:
        ```python
        @router.get("/images")
        async def get_images(current_user: Optional[Dict] = Depends(get_optional_user)):
            if current_user:
                # 인증된 사용자 로직
                user_id = current_user["user_id"]
            else:
                # 비인증 사용자 로직
                pass
        ```
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
