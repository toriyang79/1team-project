"""
파일 업로드 핸들러

비동기 파일 업로드 및 검증을 처리합니다.
"""

import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

CHUNK_SIZE = 1024 * 1024  # 1MB


async def validate_and_save_file(file: UploadFile) -> str:
    """
    파일을 검증하고 비동기로 저장합니다.

    검증 항목:
    1. 파일 확장자 검증
    2. 파일 크기 제한 (청크 단위로 체크)
    3. 안전한 파일명 생성

    Args:
        file: 업로드된 파일

    Returns:
        str: 저장된 파일의 상대 URL (/uploads/images/xxx.jpg)

    Raises:
        HTTPException: 파일이 유효하지 않을 경우
    """
    # 1. 파일 확장자 검증
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

    # 2. 안전한 파일명 생성 (UUID 사용)
    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # 3. 청크 단위 비동기 저장 + 크기 검증
    total_size = 0
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(CHUNK_SIZE):
                total_size += len(chunk)

                # 파일 크기 초과 확인
                if total_size > settings.MAX_FILE_SIZE:
                    # 파일 삭제 후 에러 발생
                    await out_file.close()
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    max_size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"파일 크기가 {max_size_mb}MB를 초과했습니다."
                    )

                await out_file.write(chunk)

    except HTTPException:
        raise
    except Exception as e:
        # 업로드 실패 시 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
        )

    # 4. 저장된 파일의 URL 반환
    return f"/uploads/images/{safe_filename}"


async def delete_file(file_url: str) -> bool:
    """
    파일을 삭제합니다.

    Args:
        file_url: 파일 URL (/uploads/images/xxx.jpg)

    Returns:
        bool: 삭제 성공 여부
    """
    try:
        # URL에서 파일명 추출 (Path Traversal 방어)
        filename = os.path.basename(file_url)
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    except Exception as e:
        print(f"파일 삭제 실패: {e}")
        return False
