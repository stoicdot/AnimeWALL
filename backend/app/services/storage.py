
"""Supabase Storage operations for AnimeWall."""

import asyncio
from functools import lru_cache
from pathlib import PurePosixPath

from supabase import Client, create_client

from app.core.config import settings


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


class StorageError(Exception):
    """Raised when a storage operation fails."""


@lru_cache(maxsize=1)
def get_storage_client() -> Client:
    """Create and cache the Supabase client."""

    if not settings.supabase_url:
        raise StorageError("Supabase URL is not configured.")

    if not settings.supabase_service_role_key:
        raise StorageError("Supabase secret key is not configured.")

    try:
        return create_client(
            settings.supabase_url,
            settings.supabase_service_role_key.get_secret_value(),
        )
    except Exception:
        raise StorageError(
            "Could not initialize Supabase Storage client."
        ) from None


def _validate_object_path(object_path: str) -> None:
    """Reject unsafe storage object paths."""

    path = PurePosixPath(object_path)

    if (
        not object_path
        or path.is_absolute()
        or "\\" in object_path
        or any(part in ("", ".", "..") for part in object_path.split("/"))
    ):
        raise StorageError("Invalid storage object path.")


async def upload_image(
    *,
    file_bytes: bytes,
    object_path: str,
    content_type: str,
) -> str:
    """Upload validated image bytes and return the storage object path."""

    _validate_object_path(object_path)

    if not file_bytes:
        raise StorageError("Cannot upload an empty file.")

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise StorageError("Unsupported image content type.")

    def _upload() -> None:
        client = get_storage_client()

        client.storage.from_(
            settings.supabase_storage_bucket
        ).upload(
            path=object_path,
            file=file_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "false",
            },
        )

    try:
        await asyncio.to_thread(_upload)
        return object_path

    except StorageError:
        raise

    except Exception:
        raise StorageError("Image upload failed.") from None


async def delete_image(*, object_path: str) -> None:
    """Delete an image from Supabase Storage."""

    _validate_object_path(object_path)

    def _delete() -> None:
        client = get_storage_client()

        client.storage.from_(
            settings.supabase_storage_bucket
        ).remove([object_path])

    try:
        await asyncio.to_thread(_delete)

    except StorageError:
        raise

    except Exception:
        raise StorageError("Image deletion failed.") from None
