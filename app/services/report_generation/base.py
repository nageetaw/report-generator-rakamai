from abc import ABC, abstractmethod


class BaseReportExporter(ABC):
    @abstractmethod
    def export(self, *, transcript: str, notes: str, output_path: str) -> None:
        """Export a report to a specific format (PDF, Markdown, etc.)"""
        raise NotImplementedError
