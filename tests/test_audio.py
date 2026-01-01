import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.audio import AudioFile
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
@patch("app.utils.storage.save_uploaded_file", new_callable=AsyncMock)
async def test_upload_audio_success(
    mock_save: AsyncMock, async_client: AsyncClient, session: AsyncSession
) -> None:
    mock_save.return_value = ("/tmp/test.mp3", "test.mp3")

    user = User(username="uploaduser", hashed_password=get_password_hash("secret"))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token("test", user.id)
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("test.mp3", b"dummy audio content", "audio/mpeg")}
    response = await async_client.post("/audio/upload", files=files, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "audio_id" in data

    result = await session.execute(
        select(AudioFile).filter(AudioFile.id == data["audio_id"])
    )
    audio = result.scalar_one_or_none()
    assert audio is not None
    assert audio.user_id == user.id
    assert audio.filename.endswith(".mp3")


@pytest.mark.asyncio
async def test_upload_audio_unauthorized(async_client: AsyncClient) -> None:
    files = {"file": ("test.mp3", b"dummy", "audio/mpeg")}
    response = await async_client.post("/audio/upload", files=files)
    assert response.status_code == 401
