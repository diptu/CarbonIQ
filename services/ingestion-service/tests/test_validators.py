"""Unit tests for the structural file validators (pure functions, no I/O)."""

from app.models.ingested_file import FileType
from app.validators.base import validate_file
from app.validators.bill import validate_bill_image, validate_bill_pdf
from app.validators.certificate import validate_certificate, validate_ppa_contract
from app.validators.nem12 import validate_nem12_csv

VALID_NEM12 = (
    "100,NEM12,202501010000,UNITEDDP,MDP1\n"
    "200,NMI0000001,E1,E1,N1,METSER123,E,,,,,20250101000000,20250101000000\n"
    "300,20250101,1,2,3,4,5,6,7,8,9,10,,,,,,,,,,,,,,A,,,,20250101000000\n"
    "900\n"
)


def test_validate_bill_pdf_accepts_well_formed_pdf():
    content = b"%PDF-1.4\n%mock pdf content"
    result = validate_bill_pdf("bill.pdf", "application/pdf", content)
    assert result.is_valid


def test_validate_bill_pdf_rejects_bad_magic_bytes():
    result = validate_bill_pdf("bill.pdf", "application/pdf", b"not a pdf")
    assert not result.is_valid
    assert any("PDF header" in e for e in result.errors)


def test_validate_bill_pdf_rejects_empty_file():
    result = validate_bill_pdf("bill.pdf", "application/pdf", b"")
    assert not result.is_valid
    assert result.errors == ["File is empty"]


def test_validate_bill_pdf_rejects_wrong_content_type():
    result = validate_bill_pdf("bill.pdf", "image/png", b"%PDF-1.4")
    assert not result.is_valid
    assert any("content-type" in e for e in result.errors)


def test_validate_bill_image_accepts_jpeg():
    content = b"\xff\xd8\xff\xe0mock jpeg bytes"
    result = validate_bill_image("bill.jpg", "image/jpeg", content)
    assert result.is_valid


def test_validate_bill_image_accepts_png():
    content = b"\x89PNG\r\n\x1a\nmock png bytes"
    result = validate_bill_image("bill.png", "image/png", content)
    assert result.is_valid


def test_validate_bill_image_rejects_unrecognized_header():
    result = validate_bill_image("bill.jpg", "image/jpeg", b"not an image")
    assert not result.is_valid
    assert any("JPEG or PNG header" in e for e in result.errors)


def test_validate_nem12_accepts_well_formed_csv():
    result = validate_nem12_csv("interval.csv", "text/csv", VALID_NEM12.encode())
    assert result.is_valid, result.errors


def test_validate_nem12_rejects_missing_header_record():
    bad = "200,NMI0000001\n900\n"
    result = validate_nem12_csv("interval.csv", "text/csv", bad.encode())
    assert not result.is_valid
    assert any("100" in e for e in result.errors)


def test_validate_nem12_rejects_missing_footer_record():
    bad = "100,NEM12\n200,NMI0000001\n"
    result = validate_nem12_csv("interval.csv", "text/csv", bad.encode())
    assert not result.is_valid
    assert any("900" in e for e in result.errors)


def test_validate_nem12_rejects_missing_nmi_record():
    bad = "100,NEM12\n900\n"
    result = validate_nem12_csv("interval.csv", "text/csv", bad.encode())
    assert not result.is_valid
    assert any("200" in e for e in result.errors)


def test_validate_nem12_rejects_empty_file():
    result = validate_nem12_csv("interval.csv", "text/csv", b"")
    assert not result.is_valid


def test_validate_certificate_accepts_pdf():
    result = validate_certificate("rec.pdf", "application/pdf", b"%PDF-1.4")
    assert result.is_valid


def test_validate_certificate_rejects_unsupported_content_type():
    result = validate_certificate("rec.exe", "application/octet-stream", b"data")
    assert not result.is_valid


def test_validate_ppa_contract_delegates_to_certificate_rules():
    result = validate_ppa_contract("ppa.pdf", "application/pdf", b"%PDF-1.4")
    assert result.is_valid


def test_validate_file_dispatches_by_file_type():
    result = validate_file(
        FileType.NEM12_CSV, "interval.csv", "text/csv", VALID_NEM12.encode()
    )
    assert result.is_valid

    result = validate_file(FileType.BILL_PDF, "bill.pdf", "application/pdf", b"not-a-pdf")
    assert not result.is_valid
