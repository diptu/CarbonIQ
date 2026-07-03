"""Structural validation for REC/LGC certificates and PPA contracts.

Registry matching (CER lookup, vintage validation) happens in
offset-service once the record reaches energy-data-service — this is just
a file-integrity gate.
"""

from app.validators.base import ValidationResult
from app.validators.bill import PDF_MAGIC

_ALLOWED_CONTENT_TYPES = {"application/pdf", "text/csv", "application/json"}


def validate_certificate(filename: str, content_type: str, content: bytes) -> ValidationResult:
    result = ValidationResult()

    if not content:
        result.add("File is empty")
        return result

    if content_type not in _ALLOWED_CONTENT_TYPES:
        result.add(
            f"Unsupported content-type: {content_type} "
            f"(expected one of {sorted(_ALLOWED_CONTENT_TYPES)})"
        )

    if content_type == "application/pdf" and not content.startswith(PDF_MAGIC):
        result.add("File does not have a valid PDF header (%PDF-)")

    return result


def validate_ppa_contract(filename: str, content_type: str, content: bytes) -> ValidationResult:
    # PPA contracts are manual + OCR uploads (per README), so they're
    # validated the same way as certificates: a non-empty PDF/CSV/JSON file.
    return validate_certificate(filename=filename, content_type=content_type, content=content)
