import uuid
from fastapi import UploadFile, HTTPException
from app.models import AudioFile
from app.repositories.audio import AudioFileRepository
from app.utils.storage import save_uploaded_file


class AudioService:
    def __init__(self, repo: AudioFileRepository):
        self.repo = repo

    async def upload_audio(self, file: UploadFile, user_id: int) -> str:
        audio_id = str(uuid.uuid4())

        try:
            file_path, file_name = await save_uploaded_file(file, user_id)

            audio = AudioFile(
                id=audio_id,
                filename=file_name,
                file_path=file_path,
                user_id=user_id,
            )

            await self.repo.create(audio)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload audio",
            ) from exc

        return audio_id
