
import hashlib
from io import BytesIO

import pytest
from PIL import Image

from app.services.image_validation import (
    ImageValidationError,
    validate_image,
)


def create_test_image(
    image_format="JPEG",
    size=(1920, 1080),
):
    buffer = BytesIO()

    image = Image.new("RGB", size, color="blue")
    image.save(buffer, format=image_format)

    return buffer.getvalue()


def test_valid_jpeg_image():
    image_bytes = create_test_image("JPEG")

    result = validate_image(image_bytes, "image/jpeg")

    assert result.width == 1920
    assert result.height == 1080
    assert result.content_type == "image/jpeg"


def test_valid_png_image():
    image_bytes = create_test_image("PNG")

    result = validate_image(image_bytes, "image/png")

    assert result.content_type == "image/png"


def test_valid_webp_image():
    image_bytes = create_test_image("WEBP")

    result = validate_image(image_bytes, "image/webp")

    assert result.content_type == "image/webp"


def test_empty_image_rejected():
    with pytest.raises(ImageValidationError):
        validate_image(b"", "image/jpeg")


def test_invalid_image_rejected():
    with pytest.raises(ImageValidationError):
        validate_image(b"this is not an image", "image/jpeg")


def test_mismatched_content_type_rejected():
    image_bytes = create_test_image("JPEG")

    with pytest.raises(ImageValidationError):
        validate_image(image_bytes, "image/png")


def test_small_image_rejected():
    image_bytes = create_test_image("JPEG", (100, 100))

    with pytest.raises(ImageValidationError):
        validate_image(image_bytes, "image/jpeg")


def test_file_size_limit():
    image_bytes = b"x" * (15 * 1024 * 1024 + 1)

    with pytest.raises(ImageValidationError):
        validate_image(image_bytes, "image/jpeg")


def test_sha256_checksum():
    image_bytes = create_test_image("PNG")

    result = validate_image(image_bytes, "image/png")

    expected_hash = hashlib.sha256(image_bytes).hexdigest()

    assert result.checksum_sha256 == expected_hash
