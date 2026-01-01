from app.api.deps import AudioServiceDep, AuthUserDep
from pydantic import BaseModel

from fastapi import APIRouter, UploadFile, status


router = APIRouter()


class AudioUploadResponse(BaseModel):
    audio_id: str


@router.post(
    "/upload", status_code=status.HTTP_201_CREATED, response_model=AudioUploadResponse
)
async def upload_audio(
    file: UploadFile, service: AudioServiceDep, current_user: AuthUserDep
) -> AudioUploadResponse:
    """Upload an audio file and create an `AudioFile` record for the current user."""

    audio = await service.upload_audio(file, current_user.id)
    return AudioUploadResponse(audio_id=audio.id)
