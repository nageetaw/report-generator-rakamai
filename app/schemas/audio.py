from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    audio_id: str
    filename: str
