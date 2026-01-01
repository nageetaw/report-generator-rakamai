import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


def ensure_upload_directory() -> Path:
    """Ensure upload directory exists and return its path."""
    upload_path = Path(settings.AUDIO_UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower()


def is_valid_audio_file(filename: str) -> bool:
    """Check if file has a valid audio extension."""
    extension = get_file_extension(filename)
    return extension in settings.ALLOWED_AUDIO_EXTENSIONS


async def save_uploaded_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    """
    Save uploaded file to disk and return (file_path, filename).

    Args:
        file: Uploaded file
        user_id: ID of the user uploading the file

    Returns:
        Tuple of (file_path, filename)
    """
    if not is_valid_audio_file(file.filename):
        raise ValueError(
            f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
        )

    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    upload_dir = ensure_upload_directory()
    user_dir = upload_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / unique_filename

    with open(file_path, "wb") as f:
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise ValueError(
                f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE} bytes"
            )
        f.write(content)

    return str(file_path), unique_filename
