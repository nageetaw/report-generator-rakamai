import json
import httpx
from typing import Dict, Any, cast

from app.services.notes_generation.base import BaseNotesGenerator
from app.core.config import settings

SYSTEM_PROMPT = """
You are an AI assistant responsible for generating a formal and structured meeting report from a given transcript.

CRITICAL CONSTRAINTS:
1. Use ONLY the information explicitly present in the transcript.
2. Do NOT add, infer, assume, or invent any information.
3. If no decisions are mentioned, write a phrase equivalent to “No decisions were made” in the same language as the transcript.
4. If no action items are mentioned, write a phrase equivalent to “No action items were identified” in the same language as the transcript.
5. Use identified speaker names if available in the transcript; otherwise, use the same speaker labels as provided.
6. Follow the output format exactly as specified.

LANGUAGE CONSTRAINT (MANDATORY):
- Use the transcript itself to determine the language.
- The entire output MUST be written in the same language as the transcript.
- All fields in the output (summary, topics_discussed, decisions_made, action_items) MUST match the transcript language.
- Do not translate or mix languages.


CONTENT REQUIREMENTS:
- The title must clearly indicate that this is a meeting report.
- The summary must be 4-5 lines long and clearly explain:
  - The purpose of the meeting (e.g., interview, discussion, review, final-year meeting, etc.)
  - The main subject or focus of the meeting
- Topics discussed must be clearly listed as distinct discussion points.
- Decisions made must include only explicitly stated decisions.
- Action items must include only explicitly stated tasks or follow-ups.

OUTPUT FORMAT (MUST MATCH EXACTLY):

Return a valid JSON object with the following structure:

{
  "title": "Meeting Report",
  "summary": "string",
  "topics_discussed": ["string"],
  "decisions_made": ["string"],
  "action_items": ["string"]
}

RULES:
- Use arrays for all list fields
- Do NOT use Markdown
- Do NOT include extra keys
- Do NOT wrap the JSON in code fences
---------------
"""


class MistralNotesGenerator(BaseNotesGenerator):
    """
    Meeting notes generator using Mistral LLM API (HTTP), forcing JSON output.
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
        """Initialize async HTTP client for Mistral API calls."""

        self._client = httpx.AsyncClient(headers=self._headers, timeout=None)
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Ensure the underlying HTTP client is closed on context exit."""

        if self._client:
            await self._client.aclose()

    async def generate(self, transcript: str) -> Dict:
        """Send transcript to Mistral and return parsed JSON notes.

        The returned value is a dict matching the required notes schema.
        """

        assert self._client is not None

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"TRANSCRIPT:\n<<<\n{transcript}\n>>>"},
        ]

        payload = {
            "model": self._model,
            "messages": messages,
            # "max_tokens": 2000,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        response = await self._client.post(
            f"{self._base_url}/chat/completions",
            json=payload,
        )

        response.raise_for_status()

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(
                f"No choices returned from Mistral LLM. status={response.status_code}, body={response.text!r}"
            )

        raw = choices[0].get("message", {}).get("content")
        if not raw:
            raise RuntimeError(
                f"Empty content returned from Mistral. Choice={choices[0]!r}"
            )

        if isinstance(raw, str):
            try:
                notes: Dict[str, Any] = cast(Dict[str, Any], json.loads(raw))
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse JSON from Mistral: {raw!r}") from e
        else:
            notes = raw

        return notes
