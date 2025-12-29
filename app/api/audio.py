from typing import Dict
import uuid

from app.api.deps import AuthUserDep, DBSessionDep
from app.models.audio import AudioFile
from app.schemas.audio import AudioUploadResponse
from app.utils.storage import save_uploaded_file
from fastapi import APIRouter, UploadFile


router = APIRouter()


@router.post("/upload", response_model=AudioUploadResponse)
async def upload_audio(
    file: UploadFile, db: DBSessionDep, current_user: AuthUserDep
) -> Dict:

    audio_id = str(uuid.uuid4())

    file_path, file_name = await save_uploaded_file(file, current_user.id)

    audio = AudioFile(
        id=audio_id, filename=file_name, file_path=file_path, user_id=current_user.id
    )

    db.add(audio)
    await db.commit()

    return {"audio_id": audio_id}
