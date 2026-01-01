import enum

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, func, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base


class JobStatus(str, enum.Enum):
    CREATED = "created"
    TRANSCRIBED = "transcribed"
    SUMMARIZED = "summarized"
    FAILED = "failed"


class AudioFile(Base):
    """Model to store details related to audio file uploaded by authenticated user."""

    __tablename__ = "audio_files"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="audio_files")
    processing_jobs = relationship(
        "AudioProcessingJob",
        back_populates="audio_file",
    )


class AudioProcessingJob(Base):
    """Model to store audio processing jobs corresponds to audio file."""

    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True)
    audio_id = Column(String, ForeignKey("audio_files.id"))
    status = Column(
        Enum(JobStatus, name="job_status_enum"),
        nullable=False,
        default=JobStatus.CREATED,
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    audio_file = relationship(
        "AudioFile",
        back_populates="processing_jobs",
    )
