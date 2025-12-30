import asyncio
from typing import Dict, Any, List
import httpx

from app.core.config import settings
from app.services.transcription.base import BaseTranscriber


class AssemblyAITranscriber(BaseTranscriber):
    """
    Transcriber implementation using the AssemblyAI API.
    """

    def __init__(self) -> None:
        self.headers = {
            "authorization": settings.ASSEMBLYAI_API_KEY,
            "content-type": "application/json",
        }
        self._client: httpx.AsyncClient | None = None
        self._base_url = settings.ASSEMBLYAI_BASE_URL
        self._poll_interval_seconds = 3

    async def __aenter__(self) -> "AssemblyAITranscriber":
        self._client = httpx.AsyncClient(
            headers=self.headers,
            timeout=None,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def transcribe(self, audio_path: str) -> Dict:
        audio_url = await self._upload_audio(audio_path)
        transcript_id = await self._request_transcription(audio_url)
        transcript_data = await self._poll_transcription(transcript_id)

        return {
            "transcript": self._format_diarized_text(transcript_data),
            "language_code": transcript_data.get("language_code"),
        }

    async def _upload_audio(self, audio_path: str) -> str:
        """
        Upload an audio file to AssemblyAI and return its hosted URL.
        """
        assert self._client is not None
        with open(audio_path, "rb") as file:
            audio_bytes = file.read()

        response = await self._client.post(
            f"{self._base_url}/upload",
            content=audio_bytes,
        )
        response.raise_for_status()
        data = response.json()
        return str(data["upload_url"])

    async def _request_transcription(self, audio_url: str) -> str:
        """
        Submit a transcription request and return the transcript ID.
        """
        assert self._client is not None
        payload = self._build_transcription_payload(audio_url)

        response = await self._client.post(
            f"{self._base_url}/transcript",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return str(data["id"])

    async def _poll_transcription(self, transcript_id: str) -> Dict[str, Any]:
        """
        Poll AssemblyAI until transcription completes or fails.
        """
        assert self._client is not None
        while True:
            response = await self._client.get(
                f"{self._base_url}/transcript/{transcript_id}"
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()

            status = data.get("status")
            if status == "completed":
                return data
            if status == "error":
                raise RuntimeError(f"AssemblyAI error: {data.get('error')}")

            await asyncio.sleep(self._poll_interval_seconds)

    def _build_transcription_payload(self, audio_url: str) -> Dict:
        """
        Build the transcription configuration payload.
        """
        return {
            "audio_url": audio_url,
            "speaker_labels": True,
            "language_detection": True,
            "punctuate": True,
            "format_text": True,
            "entity_detection": True,
            "disfluencies": False,
        }

    def _format_diarized_text(self, transcript_data: Dict[str, Any]) -> str:
        """
        Convert AssemblyAI utterances into a readable diarized transcript.
        """
        utterances: List[Dict[str, Any]] = transcript_data.get("utterances", [])

        return "\n".join(
            f"Speaker {u['speaker']}: {u['text']}" for u in utterances if u.get("text")
        )
