import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.ocr import get_ocr_obj
from app.db.session import get_db
from app.models.ocr import OCRResult

router = APIRouter(prefix="/ocr", tags=["ocr"])
logger = logging.getLogger(__name__)


# -------------------------------------
# EndPoints
# -------------------------------------
@router.get(
    "/result/{file_id}",
    response_model=JSONResponse,
    # dependencies=[Depends(require_permissions(["ocr.read"]))],
    openapi_extra={
        "summary": "Get OCR result by file ID",
        "description": "Fetches the OCR text and metadata for a given uploaded file",
        # "security": [{"BearerAuth": []}],
    },
)
async def get_ocr_result(
    file_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Retrieve OCR result for a specific file.
    """
    # Fetch OCR result or raise 404
    obj: OCRResult = await get_ocr_obj(db, file_id)

    if not obj:
        raise HTTPException(status_code=404, detail="not found")
    return {
        "file_id": obj.file_id,
        "tenant_id": obj.tenant_id,
        "org_id": obj.org_id,
        "ocr_text": obj.ocr_text,
    }
