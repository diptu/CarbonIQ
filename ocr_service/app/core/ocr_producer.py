import json

from ocr_service.app.core.config import settings
from ocr_service.app.core.kafka import init_producer


async def publish_ocr_completed(event: dict):
    """
    event: dict matching schemas.output.OCRCompletedEvent
    """
    producer = await init_producer()
    await producer.send_and_wait(
        settings.KAFKA_OCR_COMPLETED_TOPIC,
        json.dumps(event).encode(),
    )
