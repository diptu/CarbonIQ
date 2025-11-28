from sqlalchemy import Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OCRResult(Base):
    __tablename__ = "ocr_results"

    file_id = Column(String, primary_key=True, index=True)
    # tenant_id = Column(String, index=True, nullable=True)
    # org_id = Column(String, index=True, nullable=True)
    ocr_text = Column(Text, nullable=True)
