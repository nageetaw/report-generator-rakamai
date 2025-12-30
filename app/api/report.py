from typing import Dict

from app.api.deps import AuthUserDep, DBSessionDep
from app.models.audio import AudioFile
from app.services.transcription.assemblyai import AssemblyAITranscriber

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

router = APIRouter()


@router.post("/generate")
async def generate_report(
    audio_id: str, db: DBSessionDep, current_user: AuthUserDep
) -> Dict:

    result = await db.execute(
        select(AudioFile).filter(
            AudioFile.id == audio_id, AudioFile.user_id == current_user.id
        )
    )
    existing_file = result.scalar_one_or_none()
    if not existing_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file with requested id not exists",
        )

    async with AssemblyAITranscriber() as t:
        transcript_data = await t.transcribe(existing_file.file_path)
        print(transcript_data["transcript"], transcript_data["language_code"])

    return {}
