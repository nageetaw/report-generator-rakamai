from typing import Optional, cast

from app.models.audio import AudioProcessingJob, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AudioFile
from app.repositories.base import BaseRepository

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload


class AudioFileRepository(BaseRepository[AudioFile]):
    """Repository for CRUD operations on `AudioFile` model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AudioFile)


class AudioProcessingJobRepository(BaseRepository[AudioProcessingJob]):
    """Repository for `AudioProcessingJob` model and related helper queries."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AudioProcessingJob)

    async def get_with_audio(self, job_id: str) -> Optional[AudioProcessingJob]:
        """Return a job joined with its related `AudioFile` by job id."""

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
        """Update status and optional error message for a processing job."""

        query = (
            update(AudioProcessingJob)
            .where(AudioProcessingJob.id == job_id)
            .values(status=status, error_message=error)
        )

        await self.db.execute(query)
        await self.db.commit()
