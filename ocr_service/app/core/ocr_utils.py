import io
from typing import Optional

import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image


async def extract_text_from_file(file_bytes: bytes, filename: Optional[str] = None) -> str:
    """
    Simple helper that tries to handle:
    - single/multi-page PDF (via pdf2image)
    - image (PIL)
    Returns concatenated text.
    """
    # Quick detection by filename / header bytes
    name = (filename or "").lower()
    try:
        # PDF detection: filename or file magic bytes
        if name.endswith(".pdf") or (file_bytes[:4] == b"%PDF"):
            # convert PDF pages to images then OCR
            images = convert_from_bytes(file_bytes)
            texts = []
            for img in images:
                texts.append(pytesseract.image_to_string(img))
            return "\n".join(texts).strip()
        else:
            # treat as image
            img = Image.open(io.BytesIO(file_bytes))
            return pytesseract.image_to_string(img).strip()
    except Exception as e:
        # fallback: try image open
        try:
            img = Image.open(io.BytesIO(file_bytes))
            return pytesseract.image_to_string(img).strip()
        except Exception:
            raise e
