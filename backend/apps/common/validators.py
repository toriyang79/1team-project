"""
Common validators for file uploads and data validation
"""

from django.core.exceptions import ValidationError
from django.conf import settings
import magic


def validate_file_size(file):
    """
    Validate file size
    """
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 104857600)  # 100MB default
    if file.size > max_size:
        raise ValidationError(
            f'파일 크기는 {max_size / 1024 / 1024}MB를 초과할 수 없습니다.'
        )


def validate_image_file(file):
    """
    Validate image file type
    """
    validate_file_size(file)

    # Check MIME type
    file_mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer

    allowed_types = getattr(settings, 'ALLOWED_IMAGE_TYPES', [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp'
    ])

    if file_mime not in allowed_types:
        raise ValidationError(
            f'허용되지 않는 이미지 형식입니다. 허용 형식: {", ".join(allowed_types)}'
        )


def validate_audio_file(file):
    """
    Validate audio file type
    """
    validate_file_size(file)

    file_mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)

    allowed_types = getattr(settings, 'ALLOWED_AUDIO_TYPES', [
        'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4'
    ])

    if file_mime not in allowed_types:
        raise ValidationError(
            f'허용되지 않는 오디오 형식입니다. 허용 형식: {", ".join(allowed_types)}'
        )


def validate_video_file(file):
    """
    Validate video file type
    """
    validate_file_size(file)

    file_mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)

    allowed_types = getattr(settings, 'ALLOWED_VIDEO_TYPES', [
        'video/mp4', 'video/webm', 'video/ogg'
    ])

    if file_mime not in allowed_types:
        raise ValidationError(
            f'허용되지 않는 비디오 형식입니다. 허용 형식: {", ".join(allowed_types)}'
        )
