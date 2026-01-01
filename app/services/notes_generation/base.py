from abc import ABC, abstractmethod
from typing import Dict


class BaseNotesGenerator(ABC):
    @abstractmethod
    async def generate(self, transcript: str) -> Dict:
        """The method will generate the structured summary from given transcription"""
        pass
