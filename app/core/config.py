"""
애플리케이션 설정 관리

pydantic-settings를 사용하여 환경변수를 타입 안전하게 관리합니다.
"""

import json
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # ===== 애플리케이션 기본 설정 =====
    APP_NAME: str = "AI Image Community API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ===== 데이터베이스 설정 =====
    DATABASE_URL: str

    # ===== JWT 인증 설정 =====
    JWT_ALGORITHM: str = "RS256"
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str = ""  # 테스트용 (운영 환경에서는 사용 안 함)
    # 개발 전용 인증(토큰 생성) 라우트 활성화 스위치
    # 기본값은 비활성(False)이며, 로컬 개발 시에만 True로 설정하세요
    ENABLE_DEV_AUTH: bool = False

    # ===== 파일 업로드 설정 =====
    UPLOAD_DIR: str = "./uploads/images"
    MAX_FILE_SIZE: int = 10485760  # 10MB (바이트 단위)
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]

    # ===== 서버 설정 =====
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ===== CORS 설정 (선택사항) =====
    CORS_ORIGINS: List[str] = []

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        """
        허용 확장자를 파싱합니다.

        환경변수에서 JSON 배열 또는 콤마 구분 문자열을 받아 리스트로 변환합니다.
        """
        if isinstance(v, str):
            try:
                # JSON 배열 형식 시도
                return json.loads(v)
            except json.JSONDecodeError:
                # 콤마 구분 문자열 폴백
                return [ext.strip() for ext in v.split(",")]
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        CORS 오리진을 파싱합니다.

        환경변수에서 콤마 구분 문자열 또는 JSON 배열을 받아 리스트로 변환합니다.
        """
        if isinstance(v, str):
            if not v:  # 빈 문자열인 경우
                return []
            try:
                # JSON 배열 형식 시도
                return json.loads(v)
            except json.JSONDecodeError:
                # 콤마 구분 문자열 폴백
                return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# 설정 싱글톤 인스턴스
settings = Settings()
