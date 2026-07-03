"""Structural validation for AEMO NEM12 smart-meter interval CSVs.

Full semantic validation (interval math, checksum records) belongs to the
downstream parser — this is a cheap structural gate so obviously-wrong files
never get dispatched: correct record-type framing (100 header ... 900
footer) and at least one NMI data-details (200) record.
"""

import csv
import io

from app.validators.base import ValidationResult

_HEADER_RECORD = "100"
_NMI_DATA_DETAILS_RECORD = "200"
_END_OF_DATA_RECORD = "900"


def validate_nem12_csv(filename: str, content_type: str, content: bytes) -> ValidationResult:
    result = ValidationResult()

    if not content:
        result.add("File is empty")
        return result

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        result.add("File is not valid UTF-8 text")
        return result

    rows = list(csv.reader(io.StringIO(text)))
    rows = [row for row in rows if row]  # drop blank lines

    if not rows:
        result.add("CSV contains no rows")
        return result

    if rows[0][0] != _HEADER_RECORD:
        result.add(f"First record must be a '{_HEADER_RECORD}' header record")

    if rows[-1][0] != _END_OF_DATA_RECORD:
        result.add(f"Last record must be a '{_END_OF_DATA_RECORD}' end-of-data record")

    record_types = {row[0] for row in rows}
    if _NMI_DATA_DETAILS_RECORD not in record_types:
        result.add(f"File contains no '{_NMI_DATA_DETAILS_RECORD}' NMI data-details record")

    if not filename.lower().endswith(".csv"):
        result.add("Filename does not end with .csv")

    return result
