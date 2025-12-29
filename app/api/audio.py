from typing import Dict
import uuid

from app.api.deps import DBSessionDep
from app.models.audio import AudioFile
from app.schemas.audio import AudioUploadResponse

from fastapi import APIRouter, UploadFile


router = APIRouter()


@router.post("/audio", response_model=AudioUploadResponse)
def upload_audio(file: UploadFile, db: DBSessionDep) -> Dict:
    audio_id = str(uuid.uuid4())
    path = f"storage/{audio_id}.wav"

    with open(path, "wb") as f:
        f.write(file.file.read())

    audio = AudioFile(id=audio_id, filename=file.filename, file_path=path)
    db.add(audio)
    db.commit()

    return {"audio_id": audio_id, "filename": file.filename}
