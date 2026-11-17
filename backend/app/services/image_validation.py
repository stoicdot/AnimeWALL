
"""Image validation utilities for AnimeWall."""

import hashlib
import warnings
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError


MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
MIN_WIDTH = 300
MIN_HEIGHT = 300
MAX_WIDTH = 12000
MAX_HEIGHT = 12000
MAX_PIXELS = 40_000_000

ALLOWED_FORMATS = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


class ImageValidationError(ValueError):
    """Raised when an uploaded image fails validation."""


@dataclass(frozen=True)
class ImageMetadata:
    width: int
    height: int
    content_type: str
    size_bytes: int
    checksum_sha256: str


def validate_image(
    file_bytes: bytes,
    content_type: str,
) -> ImageMetadata:
    """Validate image bytes and return verified metadata."""

    if not file_bytes:
        raise ImageValidationError("Image file is empty.")

    size_bytes = len(file_bytes)

    if size_bytes > MAX_FILE_SIZE:
        raise ImageValidationError("Image size exceeds the 15 MB limit.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(BytesIO(file_bytes)) as image:
                image_format = image.format
                width, height = image.size

                if image_format not in ALLOWED_FORMATS:
                    raise ImageValidationError(
                        "Only JPEG, PNG and WebP images are allowed."
                    )

                expected_content_type = ALLOWED_FORMATS[image_format]

                if content_type.lower() != expected_content_type:
                    raise ImageValidationError(
                        "Image content type does not match its actual format."
                    )

                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    raise ImageValidationError(
                        "Image dimensions must be at least 300 x 300."
                    )

                if width > MAX_WIDTH or height > MAX_HEIGHT:
                    raise ImageValidationError(
                        "Image dimensions exceed the allowed limit."
                    )

                if width * height > MAX_PIXELS:
                    raise ImageValidationError(
                        "Image contains too many pixels."
                    )

                image.verify()

    except ImageValidationError:
        raise

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        SyntaxError,
    ) as exc:
        raise ImageValidationError(
            "Uploaded file is not a valid image."
        ) from exc

    return ImageMetadata(
        width=width,
        height=height,
        content_type=expected_content_type,
        size_bytes=size_bytes,
        checksum_sha256=hashlib.sha256(file_bytes).hexdigest(),
    )
