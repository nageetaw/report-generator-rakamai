from typing import Dict
import os

from app.api.deps import AuthUserDep, DBSessionDep
from app.models.audio import AudioFile, JobStatus
from app.services.notes_generation.mistral_notes_generator import MistralNotesGenerator
from app.services.report_generation.pdf_generator import PDFReportGenerator
from app.services.transcription.assemblyai import AssemblyAITranscriber
from app.repositories.audio_processing_job import AudioProcessingJobCRUD

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from fastapi.responses import FileResponse

router = APIRouter()


async def run_audio_processing_pipeline(
    job_id: str, audio_path: str, crud: AudioProcessingJobCRUD
) -> None:
    try:
        async with AssemblyAITranscriber() as t:
            data = await t.transcribe(audio_path)
            transcript = data["transcript"]
        await crud.update_status(job_id, JobStatus.TRANSCRIBED)

        async with MistralNotesGenerator(model="mistral-medium-latest") as generator:
            notes = await generator.generate(transcript)
        await crud.update_status(job_id, JobStatus.SUMMARIZED)

        os.makedirs("reports", exist_ok=True)
        output_path = f"reports/report_{job_id}.pdf"
        PDFReportGenerator().export(
            output_path=output_path, transcript=transcript, notes=notes
        )

        await crud.update_status(job_id, JobStatus.SUMMARIZED)

    except Exception as e:
        await crud.update_status(job_id, JobStatus.FAILED, error=str(e))


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    audio_id: str,
    db: DBSessionDep,
    current_user: AuthUserDep,
    background_tasks: BackgroundTasks,
) -> Dict:

    result = await db.execute(
        select(AudioFile).filter(
            AudioFile.id == audio_id, AudioFile.user_id == current_user.id
        )
    )
    audio_file = result.scalar_one_or_none()

    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file with requested id not exists",
        )

    path_to_process = audio_file.file_path

    crud = AudioProcessingJobCRUD(db)
    job_id = await crud.create(audio_id)

    background_tasks.add_task(
        run_audio_processing_pipeline, job_id, path_to_process, crud
    )

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Your report is being generated in the background.",
    }


@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str, db: DBSessionDep, current_user: AuthUserDep  # Your injected session
) -> Dict:
    curd = AudioProcessingJobCRUD(db)
    job = await curd.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.audio_file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return {"job_id": job.id, "status": job.status, "error": job.error_message}


@router.get("/download/{job_id}")
async def download_report(
    job_id: str, current_user: AuthUserDep, db: DBSessionDep
) -> FileResponse:
    curd = AudioProcessingJobCRUD(db)
    job = await curd.get(job_id)

    if not job or job.status != JobStatus.SUMMARIZED:
        raise HTTPException(status_code=404, detail="Report not ready or not found")

    if job.audio_file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    file_path = f"reports/report_{job_id}.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(
        path=file_path,
        filename=f"meeting_summary_{job_id}.pdf",
        media_type="application/pdf",
    )
