from typing import Optional
from pydantic import BaseModel


class ReportCreate(BaseModel):
    audio_id: str


class ReportCreateOut(BaseModel):
    job_id: str
    status: str
    message: str


class AudioJobStatusOut(BaseModel):
    job_id: str
    status: str
    error: Optional[str]
