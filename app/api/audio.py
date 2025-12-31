from typing import Dict

from app.api.deps import AuthUserDep, DBSessionDep
from app.schemas.audio import AudioUploadResponse
from app.repositories.audio import AudioFileRepository
from app.services.audio import AudioService

from fastapi import APIRouter, UploadFile


router = APIRouter()


@router.post("/upload", response_model=AudioUploadResponse)
async def upload_audio(
    file: UploadFile, db: DBSessionDep, current_user: AuthUserDep
) -> Dict:

    repo = AudioFileRepository(db)
    service = AudioService(repo)

    audio_id = await service.upload_audio(file, current_user.id)

    return AudioUploadResponse(audio_id=audio_id)
