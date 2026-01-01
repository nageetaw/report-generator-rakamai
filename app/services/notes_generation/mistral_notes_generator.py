import httpx
from typing import Dict, Any

from app.services.notes_generation.base import BaseNotesGenerator
from app.core.config import settings


class MistralNotesGenerator(BaseNotesGenerator):
    """
    Meeting notes generator using Mistral LLM API
    """

    def __init__(self, model: str) -> None:
        self._model = model
        self._client: httpx.AsyncClient | None = None
        self._base_url = settings.MISTRAL_BASE_URL
        self._headers = {
            "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }

    async def __aenter__(self) -> "MistralNotesGenerator":
        self._client = httpx.AsyncClient(headers=self._headers, timeout=None)
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def generate(self, transcript: str) -> str:
        assert self._client is not None

        prompt = (
            "Generate a structured meeting summary from the transcript below. "
            "Include:\n"
            "- Topics discussed\n"
            "- Decisions made\n"
            "- Action items\n\n"
            f"Transcript:\n{transcript}"
        )

        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,  # for experimenting
            "temperature": 0.3,  # for experimenting
        }

        response = await self._client.post(
            f"{self._base_url}/chat/completions",
            json=payload,
        )

        response.raise_for_status()

        data: Dict[str, Any] = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("No response from Mistral LLM")

        return str(choices[0]["message"]["content"])
