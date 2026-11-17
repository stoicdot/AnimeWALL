
from unittest.mock import MagicMock, patch

import pytest

from app.services.storage import (
    StorageError,
    upload_image,
    delete_image,
)


@pytest.mark.asyncio
async def test_upload_image_successfully():
    with patch("app.services.storage.get_storage_client") as mock_client:
        storage = MagicMock()
        bucket = MagicMock()

        mock_client.return_value = storage
        storage.storage.from_.return_value = bucket

        result = await upload_image(
            file_bytes=b"fake-image-data",
            object_path="wallpapers/test/original.jpg",
            content_type="image/jpeg",
        )

        assert result == "wallpapers/test/original.jpg"
        bucket.upload.assert_called_once()


@pytest.mark.asyncio
async def test_upload_rejects_empty_file():
    with pytest.raises(StorageError):
        await upload_image(
            file_bytes=b"",
            object_path="wallpapers/test/original.jpg",
            content_type="image/jpeg",
        )


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_content_type():
    with pytest.raises(StorageError):
        await upload_image(
            file_bytes=b"fake-data",
            object_path="wallpapers/test/original.gif",
            content_type="image/gif",
        )


@pytest.mark.asyncio
async def test_upload_rejects_unsafe_object_path():
    with pytest.raises(StorageError):
        await upload_image(
            file_bytes=b"fake-data",
            object_path="../secret.jpg",
            content_type="image/jpeg",
        )


@pytest.mark.asyncio
async def test_delete_image_successfully():
    with patch("app.services.storage.get_storage_client") as mock_client:
        storage = MagicMock()
        bucket = MagicMock()

        mock_client.return_value = storage
        storage.storage.from_.return_value = bucket

        await delete_image(
            object_path="wallpapers/test/original.jpg"
        )

        bucket.remove.assert_called_once_with(
            ["wallpapers/test/original.jpg"]
        )


@pytest.mark.asyncio
async def test_delete_rejects_unsafe_object_path():
    with pytest.raises(StorageError):
        await delete_image(
            object_path="../secret.jpg"
        )


@pytest.mark.asyncio
async def test_upload_storage_failure():
    with patch(
        "app.services.storage.get_storage_client",
        side_effect=RuntimeError("Storage unavailable"),
    ):
        with pytest.raises(StorageError, match="Image upload failed"):
            await upload_image(
                file_bytes=b"fake-image-data",
                object_path="wallpapers/test/original.jpg",
                content_type="image/jpeg",
            )
