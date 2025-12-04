"""
파일 업로드/삭제 헬퍼

이 모듈은 '로컬 디스크'와 'AWS S3' 두 가지 백엔드를 지원합니다.

핵심 아이디어
- STORAGE_BACKEND가 'local'이면 기존처럼 ./uploads 디렉토리에 저장합니다.
- STORAGE_BACKEND가 's3'이면 S3 버킷/prefix로 업로드하고 공개 URL을 반환합니다.

주의사항 (초보자용 설명)
- 이미지 확장자와 최대 크기를 먼저 검증합니다.
- S3 업로드 시에는 메모리에 한 번 담아 put_object로 업로드합니다.
  (기본 최대 10MB라서 메모리 사용량이 크지 않습니다.)
- 반환되는 URL은 프론트엔드에서 바로 사용할 수 있는 공개 URL입니다.
  - CloudFront/CDN을 쓰는 경우 AWS_S3_PUBLIC_URL을 세팅하세요.
  - 아니면 표준 S3 URL을 자동으로 만듭니다.
"""

import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

CHUNK_SIZE = 1024 * 1024  # 1MB

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except Exception:  # 로컬에서 즉시 boto3가 없을 수 있으므로 임포트 에러는 런타임까지 보류
    boto3 = None
    BotoCoreError = ClientError = Exception


async def _read_and_validate(file: UploadFile) -> tuple[str, bytes]:
    """
    업로드 파일을 읽으면서 확장자/크기를 검증하고, 안전한 파일명을 생성합니다.

    Returns:
        (safe_filename, content_bytes)
    """
    # 1) 파일명/확장자 검증
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일명이 없습니다."
        )

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않는 파일 형식입니다. 허용: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 2) 안전한 파일명 생성 (UUID 사용)
    safe_filename = f"{uuid.uuid4().hex}.{ext}"

    # 3) 크기 검증을 하며 메모리에 적재 (10MB 기본 제한)
    total_size = 0
    chunks: list[bytes] = []
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"파일 크기가 {max_size_mb}MB를 초과했습니다."
            )
        chunks.append(chunk)

    content = b"".join(chunks)
    return safe_filename, content


def _build_s3_key(filename: str) -> str:
    """버킷 내에 저장할 오브젝트 키를 생성합니다.

    예: prefix='uploads/images', filename='abc.jpg' -> 'uploads/images/abc.jpg'
    (prefix 끝에 슬래시가 있으면 제거합니다.)
    """
    prefix = settings.AWS_S3_PREFIX.strip("/") if settings.AWS_S3_PREFIX else ""
    return f"{prefix}/{filename}" if prefix else filename


def _build_s3_url(key: str) -> str:
    """최종 공개 URL을 만듭니다.

    우선 순위:
    1) AWS_S3_PUBLIC_URL이 설정되면 해당 값 기반: '{PUBLIC_URL}/{key}'
    2) 커스텀 엔드포인트(예: Minio)가 있으면: '{endpoint}/{bucket}/{key}'
    3) AWS 표준: 'https://{bucket}.s3.{region}.amazonaws.com/{key}'
    """
    public_base = settings.AWS_S3_PUBLIC_URL.strip("/") if settings.AWS_S3_PUBLIC_URL else ""
    if public_base:
        return f"{public_base}/{key}"

    if settings.AWS_S3_ENDPOINT_URL:
        base = settings.AWS_S3_ENDPOINT_URL.rstrip("/")
        return f"{base}/{settings.AWS_S3_BUCKET}/{key}"

    # 표준 AWS S3 URL
    region = settings.AWS_REGION or "ap-northeast-2"
    return f"https://{settings.AWS_S3_BUCKET}.s3.{region}.amazonaws.com/{key}"


async def validate_and_save_file(file: UploadFile) -> str:
    """
    파일을 검증하고 저장합니다.

    - STORAGE_BACKEND == 'local': ./uploads/images 에 저장하고 '/uploads/images/...' URL을 반환합니다.
    - STORAGE_BACKEND == 's3': S3 버킷에 업로드하고 공개 URL을 반환합니다.
    """
    # 공통: 파일 검증 + 메모리에 적재
    safe_filename, content = await _read_and_validate(file)

    # 로컬 저장소
    if settings.STORAGE_BACKEND.lower() == "local":
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        try:
            # 비동기 파일 저장
            async with aiofiles.open(file_path, "wb") as out_file:
                await out_file.write(content)
        except Exception as e:
            # 업로드 실패 시 파일 삭제
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
            )

        # 정적 경로(URL) 반환 (StaticFiles로 서빙됨)
        return f"/uploads/images/{safe_filename}"

    # S3 저장소
    if settings.STORAGE_BACKEND.lower() == "s3":
        if boto3 is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="boto3가 설치되어 있지 않습니다. requirements.txt를 확인하세요."
            )

        # S3 클라이언트 생성 (EC2에선 IAM Role 사용, 로컬은 환경변수 키 사용)
        s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION or None,
            endpoint_url=(settings.AWS_S3_ENDPOINT_URL or None) or None,
        )

        key = _build_s3_key(safe_filename)
        # ExtraArgs 구성: ContentType은 있으면 추가
        extra: dict = {}
        if getattr(file, "content_type", None):
            extra["ContentType"] = file.content_type

        # 버킷에서 ACL이 금지(Bucket owner enforced)된 경우가 있으므로,
        # 값이 비어있지 않을 때만 ACL을 넣고, 실패 시 ACL 없이 재시도합니다.
        acl_value = (settings.AWS_S3_ACL or "").strip()
        if acl_value:
            extra["ACL"] = acl_value

        try:
            s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key=key, Body=content, **extra)
        except ClientError as e:
            # ACL이 금지된 버킷일 때의 에러에 대해 한 번 더 시도 (ACL 제거)
            err_code = e.response.get("Error", {}).get("Code", "") if hasattr(e, "response") else ""
            msg = str(e)
            acl_in_extra = "ACL" in extra
            if acl_in_extra and (err_code in {"AccessControlListNotSupported", "InvalidRequest"} or "ACL" in msg):
                try:
                    extra.pop("ACL", None)
                    s3.put_object(Bucket=settings.AWS_S3_BUCKET, Key=key, Body=content, **extra)
                except (BotoCoreError, ClientError) as e2:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"S3 업로드 실패: {str(e2)}"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"S3 업로드 실패: {str(e)}"
                )
        except BotoCoreError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 업로드 실패: {str(e)}"
            )

        # 최종 접근 가능한 URL 구성
        return _build_s3_url(key)

    # 지원하지 않는 스토리지 백엔드 값
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="올바르지 않은 STORAGE_BACKEND 값입니다. 'local' 또는 's3'로 설정하세요."
    )


async def delete_file(file_url: str) -> bool:
    """
    파일을 삭제합니다.

    - 로컬: '/uploads/images/...' 형태의 URL에서 파일명을 추출해 삭제합니다.
    - S3: 공개 URL에서 오브젝트 키를 추출해 삭제합니다.

    삭제는 실패해도 서비스 전체에 치명적이지 않으므로, 오류 시 False를 반환합니다.
    """
    try:
        backend = settings.STORAGE_BACKEND.lower()

        # 1) 로컬 파일 삭제
        if backend == "local" or file_url.startswith("/uploads/"):
            filename = os.path.basename(file_url)  # Path Traversal 방어
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False

        # 2) S3 오브젝트 삭제
        if backend == "s3":
            if boto3 is None:
                return False

            # URL -> key 추출
            key = _extract_s3_key_from_url(file_url)
            if not key:
                return False

            s3 = boto3.client(
                "s3",
                region_name=settings.AWS_REGION or None,
                endpoint_url=(settings.AWS_S3_ENDPOINT_URL or None) or None,
            )
            try:
                s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
                return True
            except (BotoCoreError, ClientError):
                return False

        return False

    except Exception as e:
        print(f"파일 삭제 실패: {e}")
        return False


def _extract_s3_key_from_url(url: str) -> str | None:
    """
    S3 공개 URL로부터 오브젝트 키를 추출합니다.

    처리 우선 순위:
    1) AWS_S3_PUBLIC_URL이 설정되어 있고, 그로 시작하면 해당 베이스를 제거한 나머지를 key로 사용
    2) 커스텀 엔드포인트(예: Minio)라면 '{endpoint}/{bucket}/...' 패턴 처리
    3) 표준 AWS S3 URL 'https://{bucket}.s3.{region}.amazonaws.com/{key}' 처리
    """
    try:
        # 1) PUBLIC_URL 기반
        if settings.AWS_S3_PUBLIC_URL:
            base = settings.AWS_S3_PUBLIC_URL.rstrip("/")
            if url.startswith(base + "/"):
                return url[len(base) + 1 :]

        # 2) 커스텀 엔드포인트
        if settings.AWS_S3_ENDPOINT_URL:
            base = settings.AWS_S3_ENDPOINT_URL.rstrip("/")
            prefix = f"{base}/{settings.AWS_S3_BUCKET}/"
            if url.startswith(prefix):
                return url[len(prefix) :]

        # 3) 표준 AWS S3 URL
        #    예: https://mybucket.s3.ap-northeast-2.amazonaws.com/uploads/images/abc.jpg
        #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #         이 부분을 제거하고 나머지를 key로 사용
        region = settings.AWS_REGION or "ap-northeast-2"
        std_prefix = f"https://{settings.AWS_S3_BUCKET}.s3.{region}.amazonaws.com/"
        if url.startswith(std_prefix):
            return url[len(std_prefix) :]

        return None
    except Exception:
        return None
