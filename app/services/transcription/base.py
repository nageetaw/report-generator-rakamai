from abc import ABC, abstractmethod
from typing import Dict


class BaseTranscriber(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str) -> Dict:
        pass
