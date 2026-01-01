from typing import Dict
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from unittest.mock import AsyncMock
from types import SimpleNamespace

from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from fastapi import HTTPException, status
from app.api import deps
from main import app


@pytest.mark.asyncio
async def test_generate_report_success(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    user = User(username="reportuser", hashed_password=get_password_hash("secret"))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token("test", user.id)
    headers = {"Authorization": f"Bearer {token}"}

    mock_service = SimpleNamespace(
        create_bg_task=AsyncMock(
            return_value={"job_id": "job-123", "status": "created", "message": "queued"}
        )
    )

    app.dependency_overrides[deps.get_audio_processing_job_service] = (
        lambda: mock_service
    )

    response = await async_client.post(
        "/report/generate", json={"audio_id": "audio-1"}, headers=headers
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["job_id"] == "job-123"

    app.dependency_overrides.pop(deps.get_audio_processing_job_service, None)


@pytest.mark.asyncio
async def test_generate_report_audio_missing(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    user = User(username="missinguser", hashed_password=get_password_hash("secret"))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token("test", user.id)
    headers = {"Authorization": f"Bearer {token}"}

    mock_service = SimpleNamespace(
        create_bg_task=AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Audio file not found")
        )
    )

    app.dependency_overrides[deps.get_audio_processing_job_service] = (
        lambda: mock_service
    )

    response = await async_client.post(
        "/report/generate", json={"audio_id": "nope"}, headers=headers
    )
    assert response.status_code == 404

    app.dependency_overrides.pop(deps.get_audio_processing_job_service, None)


@pytest.mark.asyncio
async def test_get_job_status_not_found(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    user = User(username="notfounduser", hashed_password=get_password_hash("secret"))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token("test", user.id)
    headers = {"Authorization": f"Bearer {token}"}

    mock_service = SimpleNamespace(
        get_job_status=AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Job not found")
        )
    )

    app.dependency_overrides[deps.get_audio_processing_job_service] = (
        lambda: mock_service
    )

    response = await async_client.get("/report/status/does-not-exist", headers=headers)
    assert response.status_code == 404

    app.dependency_overrides.pop(deps.get_audio_processing_job_service, None)


@pytest.mark.asyncio
async def test_get_job_status_success(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    user = User(username="statususer", hashed_password=get_password_hash("secret"))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token("test", user.id)
    headers = {"Authorization": f"Bearer {token}"}

    mock_service = SimpleNamespace(
        get_job_status=AsyncMock(
            return_value={"job_id": "job-123", "status": "summarized", "error": None}
        )
    )

    app.dependency_overrides[deps.get_audio_processing_job_service] = (
        lambda: mock_service
    )

    response = await async_client.get("/report/status/job-123", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "summarized"

    app.dependency_overrides.pop(deps.get_audio_processing_job_service, None)


@pytest.mark.asyncio
async def test_download_report_not_ready(
    async_client: AsyncClient, session: AsyncSession
) -> None:
    user = User(username="downloaduser", hashed_password=get_password_hash("secret"))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token("test", user.id)
    headers = {"Authorization": f"Bearer {token}"}

    async def _download(*args: tuple, **kwargs: Dict) -> None:
        raise HTTPException(status_code=404, detail="Report not ready")

    mock_service = SimpleNamespace(download_report=AsyncMock(side_effect=_download))

    app.dependency_overrides[deps.get_audio_processing_job_service] = (
        lambda: mock_service
    )

    response = await async_client.get("/report/download/job-404", headers=headers)
    assert response.status_code == 404

    app.dependency_overrides.pop(deps.get_audio_processing_job_service, None)
