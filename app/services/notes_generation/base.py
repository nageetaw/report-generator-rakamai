from abc import ABC, abstractmethod


class BaseNotesGenerator(ABC):
    @abstractmethod
    async def generate(self, transcript: str) -> str:
        """The method will generate the structured summary from given transcription"""
        pass
