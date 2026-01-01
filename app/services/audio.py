from typing import Dict
import os
import uuid

from app.core.config import Settings
from app.models.audio import AudioFile, AudioProcessingJob, JobStatus
from app.repositories.audio import AudioFileRepository, AudioProcessingJobRepository
from app.schemas.report import ReportCreate
from app.services.notes_generation.mistral_notes_generator import MistralNotesGenerator
from app.services.report_generation.pdf_generator import PDFReportGenerator
from app.services.transcription.assemblyai import AssemblyAITranscriber
from app.utils.storage import save_uploaded_file


from fastapi import UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse


class AudioService:
    def __init__(self, repo: AudioFileRepository):
        self.repo = repo

    async def upload_audio(self, file: UploadFile, user_id: int) -> AudioFile:
        try:
            file_path, file_name = await save_uploaded_file(file, user_id)

            audio = AudioFile(
                id=str(uuid.uuid4()),
                filename=file_name,
                file_path=file_path,
                user_id=user_id,
            )

            await self.repo.create(audio)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload audio",
            ) from exc

        return audio


class AudioProcessingJobService:
    def __init__(
        self,
        repo: AudioProcessingJobRepository,
        audio_repo: AudioFileRepository,
        background_tasks: BackgroundTasks,
    ):
        self.repo = repo
        self.audio_repo = audio_repo
        self.background_tasks = background_tasks

    async def run_audio_processing_pipeline(
        self,
        job_id: str,
        audio_path: str,
    ) -> None:
        try:
            async with AssemblyAITranscriber() as t:
                data = await t.transcribe(audio_path)
                transcript = data["transcript"]
            await self.repo.update_status(job_id, JobStatus.TRANSCRIBED)

            async with MistralNotesGenerator(
                model=Settings.DEFAULT_MISTRAL_MODEL
            ) as generator:
                notes = await generator.generate(transcript)
            await self.repo.update_status(job_id, JobStatus.SUMMARIZED)

            os.makedirs("reports", exist_ok=True)
            output_path = f"{Settings.DEFAULT_REPORT_DIR}/report_{job_id}.pdf"
            PDFReportGenerator().export(
                output_path=output_path, transcript=transcript, notes=notes
            )

        except Exception as e:
            await self.repo.update_status(job_id, JobStatus.FAILED, error=str(e))

    async def create_bg_task(self, report_create: ReportCreate) -> Dict:
        audio_id = report_create.audio_id

        audio_file = await self.audio_repo.get(audio_id)

        if audio_file is None:
            raise HTTPException(status_code=404, detail="Audio file not found")

        file_path = audio_file.file_path
        job = AudioProcessingJob(
            id=str(uuid.uuid4()), audio_id=audio_id, status=JobStatus.CREATED
        )
        job = await self.repo.create(job)
        job_id = job.id

        self.background_tasks.add_task(
            self.run_audio_processing_pipeline, job_id, file_path
        )
        return {
            "job_id": job_id,
            "status": JobStatus.CREATED,
            "message": "Your report is being generated.",
        }

    async def get_job_status(self, job_id: str) -> Dict:
        job = await self.repo.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"job_id": job_id, "status": job.status, "error": job.error_message}

    async def download_report(self, job_id: str) -> FileResponse:
        job = await self.repo.get(job_id)
        if not job or job.status != JobStatus.SUMMARIZED:
            raise HTTPException(status_code=404, detail="Report not ready or not found")

        file_path = f"{Settings.DEFAULT_REPORT_DIR}/report_{job_id}.pdf"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File missing on server")

        return FileResponse(
            path=file_path,
            filename=f"meeting_summary_{job_id}.pdf",
            media_type="application/pdf",
        )
