from app.api.deps import AudioProcessJobServiceDep, AuthUserDep
from app.schemas.report import AudioJobStatusOut, ReportCreate, ReportCreateOut

from fastapi import APIRouter, status
from fastapi.responses import FileResponse

router = APIRouter()


@router.post(
    "/generate", status_code=status.HTTP_202_ACCEPTED, response_model=ReportCreateOut
)
async def generate_report(
    report_create: ReportCreate,
    current_user: AuthUserDep,
    service: AudioProcessJobServiceDep,
) -> ReportCreateOut:
    """Create a background processing job for the provided audio id.

    Returns the created job metadata (id, status, message).
    """

    response = await service.create_bg_task(report_create=report_create)
    return ReportCreateOut(**response)


@router.get(
    "/status/{job_id}", status_code=status.HTTP_200_OK, response_model=AudioJobStatusOut
)
async def get_job_status(
    job_id: str, service: AudioProcessJobServiceDep, current_user: AuthUserDep
) -> AudioJobStatusOut:
    """Return the current status and any error for a processing job."""

    result = await service.get_job_status(job_id)
    return AudioJobStatusOut(**result)


@router.get("/download/{job_id}", status_code=status.HTTP_200_OK)
async def download_report(
    job_id: str, current_user: AuthUserDep, service: AudioProcessJobServiceDep
) -> FileResponse:
    """Return the generated PDF report file for the given job id."""

    return await service.download_report(job_id=job_id)
