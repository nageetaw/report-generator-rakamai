from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AudioFile
from app.repositories.base import BaseRepository


class AudioFileRepository(BaseRepository[AudioFile]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AudioFile)
