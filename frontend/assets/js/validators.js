"""
Validation utilities
"""

from typing import Set


def validateFileType(filename: str, allowedExtensions: Set[str]) -> bool:
    """Validate file extension"""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in allowedExtensions)


def validateFileSize(fileSize: int, maxSizeBytes: int) -> bool:
    """Validate file size"""
    return fileSize <= maxSizeBytes


def validateImageFile(file: 'File') -> tuple[bool, str]:
    """
    Comprehensive image file validation

    Args:
        file: File object from input

    Returns:
        tuple: (is_valid, error_message)
    """
    # Allowed image types
    allowedTypes = [
        "image/png", "image/jpg", "image/jpeg",
        "image/gif", "image/bmp", "image/webp"
    ]

    # Check file type
    if file.type not in allowedTypes:
        return False, "Định dạng file không được hỗ trợ. Vui lòng chọn file ảnh."

    # Check file size (16MB)
    maxSize = 16 * 1024 * 1024  # 16MB
    if file.size > maxSize:
        return False, "File quá lớn. Vui lòng chọn file nhỏ hơn 16MB."

    return True, ""
