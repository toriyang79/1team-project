"""
애플리케이션 설정 관리

pydantic-settings를 사용하여 환경변수를 타입 안전하게 관리합니다.
"""

import json
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ===== CORS 허용 오리진 목록 =====
CORS_ALLOWED_ORIGINS = [
    # 개발자 로컬 주소 (테스트용)
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # 실제 프론트엔드 배포 주소
    "http://43.200.134.109:5173",
]


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
    # STORAGE_BACKEND가 'local'이면 로컬 디스크에 저장, 's3'이면 AWS S3에 저장합니다.
    STORAGE_BACKEND: str = "local"  # 'local' | 's3'
    UPLOAD_DIR: str = "./uploads/images"
    MAX_FILE_SIZE: int = 10485760  # 10MB (바이트 단위)
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]

    # ===== S3 설정 (STORAGE_BACKEND='s3'일 때 사용) =====
    # 참고: EC2에서는 인스턴스 프로파일(IAM Role) 사용을 권장하며,
    #       로컬 개발에서는 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY를 로컬 환경변수로 설정하세요.
    AWS_REGION: str = ""
    AWS_S3_BUCKET: str = ""
    # 버킷 내 저장 경로 프리픽스. 예: "uploads/images" (끝에 슬래시 없이)
    AWS_S3_PREFIX: str = "uploads/images"
    # 업로드 시 부여할 ACL. 퍼블릭 접근이 필요한 경우 'public-read'. 사내/비공개는 'private'.
    AWS_S3_ACL: str = "public-read"
    # 커스텀 엔드포인트(Minio 등) 사용 시 설정. 비어있으면 AWS 기본 엔드포인트 사용.
    AWS_S3_ENDPOINT_URL: str = ""
    # 공개 URL 베이스를 오버라이드하고 싶을 때 사용 (예: CloudFront 도메인).
    # 설정 시: 최종 URL = f"{AWS_S3_PUBLIC_URL}/{key}"
    AWS_S3_PUBLIC_URL: str = ""

    # ===== 서버 설정 =====
    HOST: str = "0.0.0.0"
    PORT: int = 8000

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

    # 하위 호환/별칭 지원: 사용자가 S3_BUCKET_NAME, S3_BASE_URL을 설정했을 경우 매핑
    @field_validator("AWS_S3_BUCKET", mode="before")
    @classmethod
    def alias_bucket_env(cls, v):
        if v:
            return v
        import os
        return os.getenv("S3_BUCKET_NAME", "")

    @field_validator("AWS_S3_PUBLIC_URL", mode="before")
    @classmethod
    def alias_public_url_env(cls, v):
        if v:
            return v
        import os
        return os.getenv("S3_BASE_URL", "")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# 설정 싱글톤 인스턴스
settings = Settings()
