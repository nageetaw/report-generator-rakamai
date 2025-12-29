from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime

from app.db.base import Base


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
