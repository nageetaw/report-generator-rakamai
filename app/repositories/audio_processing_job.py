import uuid
from typing import Optional, cast
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audio import AudioProcessingJob, JobStatus


class AudioProcessingJobCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, audio_id: str) -> str:
        job_id = str(uuid.uuid4())
        new_job = AudioProcessingJob(
            id=job_id, audio_id=audio_id, status=JobStatus.CREATED
        )
        self.db.add(new_job)
        await self.db.commit()
        return job_id

    async def get(self, job_id: str) -> Optional[AudioProcessingJob]:
        query = (
            select(AudioProcessingJob)
            .options(selectinload(AudioProcessingJob.audio_file))
            .where(AudioProcessingJob.id == job_id)
        )
        result = await self.db.execute(query)
        return cast(Optional[AudioProcessingJob], result.scalar_one_or_none())

    async def update_status(
        self, job_id: str, status: JobStatus, error: Optional[str] = None
    ) -> None:
        query = (
            update(AudioProcessingJob)
            .where(AudioProcessingJob.id == job_id)
            .values(status=status, error_message=error)
        )
        await self.db.execute(query)
        await self.db.commit()
