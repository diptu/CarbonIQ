from uuid import UUID

from ocr_service.app.models.ocr import OCRResult
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ocr import OCRResult


async def save_ocr_result(db: AsyncSession, data: dict) -> OCRResult:
    """
    data: {file_id, tenant_id, org_id, ocr_text}
    """
    obj = OCRResult(
        file_id=data["file_id"],
        tenant_id=data.get("tenant_id"),
        org_id=data.get("org_id"),
        ocr_text=data.get("ocr_text", ""),
    )
    db.add(obj)
    await db.commit()
    # refresh to get any defaults (optional)
    await db.refresh(obj)
    return obj


async def get_ocr_obj(db: AsyncSession, file_id: UUID) -> OCRResult | None:
    """
    Fetch OCRResult by file_id.
    Returns None if not found.
    """
    result = await db.execute(select(OCRResult).where(OCRResult.file_id == file_id))
    return result.scalar_one_or_none()
