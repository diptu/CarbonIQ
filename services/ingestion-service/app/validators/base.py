"""Shared validation result type + the file_type -> validator dispatch table."""

from dataclasses import dataclass, field

from app.models.ingested_file import FileType


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def add(self, message: str) -> None:
        self.errors.append(message)


def validate_file(
    file_type: FileType, filename: str, content_type: str, content: bytes
) -> ValidationResult:
    from app.validators.bill import validate_bill_image, validate_bill_pdf
    from app.validators.certificate import (
        validate_certificate,
        validate_ppa_contract,
    )
    from app.validators.nem12 import validate_nem12_csv

    dispatch = {
        FileType.BILL_PDF: validate_bill_pdf,
        FileType.BILL_IMAGE: validate_bill_image,
        FileType.NEM12_CSV: validate_nem12_csv,
        FileType.REC_CERTIFICATE: validate_certificate,
        FileType.LGC_CERTIFICATE: validate_certificate,
        FileType.PPA_CONTRACT: validate_ppa_contract,
    }
    validator = dispatch[file_type]
    return validator(filename=filename, content_type=content_type, content=content)
