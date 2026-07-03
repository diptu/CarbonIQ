"""Structural validation for uploaded electricity/gas bills (PDF or image)."""

from app.validators.base import ValidationResult

PDF_MAGIC = b"%PDF-"
_JPEG_MAGIC = b"\xff\xd8\xff"
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/heic"}


def validate_bill_pdf(filename: str, content_type: str, content: bytes) -> ValidationResult:
    result = ValidationResult()

    if not content:
        result.add("File is empty")
        return result

    if content_type != "application/pdf":
        result.add(f"Expected content-type application/pdf, got {content_type}")

    if not content.startswith(_PDF_MAGIC):
        result.add("File does not have a valid PDF header (%PDF-)")

    if not filename.lower().endswith(".pdf"):
        result.add("Filename does not end with .pdf")

    return result


def validate_bill_image(filename: str, content_type: str, content: bytes) -> ValidationResult:
    result = ValidationResult()

    if not content:
        result.add("File is empty")
        return result

    if content_type not in _ALLOWED_IMAGE_CONTENT_TYPES:
        result.add(
            f"Unsupported image content-type: {content_type} "
            f"(expected one of {sorted(_ALLOWED_IMAGE_CONTENT_TYPES)})"
        )

    is_jpeg = content.startswith(_JPEG_MAGIC)
    is_png = content.startswith(_PNG_MAGIC)
    if not (is_jpeg or is_png):
        result.add("File does not have a recognized JPEG or PNG header")

    return result
