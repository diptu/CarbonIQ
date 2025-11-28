import json
from typing import Optional

from aiokafka import AIOKafkaConsumer
from ocr_service.app.core.config import settings
from ocr_service.app.core.kafka import close_consumer, create_consumer
from ocr_service.app.core.ocr_producer import publish_ocr_completed
from ocr_service.app.core.ocr_utils import extract_text_from_file  # we'll add this helper below
from ocr_service.app.crud.ocr import save_ocr_result
from ocr_service.app.db.session import SessionLocal


async def consume_raw_files_loop():
    """
    Background loop: consume uploads.raw_files, process OCR, store result and publish uploads.ocr_completed.
    """
    consumer: AIOKafkaConsumer = await create_consumer(settings.KAFKA_RAW_TOPIC)
    try:
        async for msg in consumer:
            try:
                payload = json.loads(msg.value)
            except Exception as e:
                print("[OCRConsumer] invalid message", e)
                continue

            file_id = payload.get("file_id")
            local_path = payload.get("local_path")
            s3_key = payload.get("s3_key")
            tenant_id = payload.get("tenant_id")
            org_id = payload.get("org_id")

            print(
                f"[OCRConsumer] processing file_id={file_id} local_path={local_path} s3_key={s3_key}"
            )

            # Fetch bytes: prefer local_path for MVP
            file_bytes: Optional[bytes] = None
            if local_path:
                try:
                    with open(local_path, "rb") as f:
                        file_bytes = f.read()
                except Exception as e:
                    print(f"[OCRConsumer] failed to read local file {local_path}: {e}")
                    file_bytes = None
            # s3_key support (optional)
            if not file_bytes and s3_key and settings.AWS_S3_BUCKET:
                # minimal S3 fetch using boto3
                import boto3

                s3 = boto3.client("s3")
                try:
                    resp = s3.get_object(Bucket=settings.AWS_S3_BUCKET, Key=s3_key)
                    file_bytes = resp["Body"].read()
                except Exception as e:
                    print("[OCRConsumer] S3 fetch failed:", e)

            if not file_bytes:
                print("[OCRConsumer] no file bytes available; skipping")
                continue

            # extract text (handles images and PDFs)
            try:
                ocr_text = await extract_text_from_file(
                    file_bytes, filename=local_path or s3_key or file_id
                )
            except Exception as e:
                print("[OCRConsumer] OCR extraction failed:", e)
                ocr_text = ""

            # store OCR result in DB
            async with SessionLocal() as session:
                try:
                    await save_ocr_result(
                        session,
                        {
                            "file_id": file_id,
                            "tenant_id": tenant_id,
                            "org_id": org_id,
                            "ocr_text": ocr_text,
                        },
                    )
                except Exception as e:
                    print("[OCRConsumer] DB save failed:", e)

            # publish event for normalization
            out_event = {
                "file_id": file_id,
                "tenant_id": tenant_id,
                "org_id": org_id,
                "ocr_text": ocr_text,
            }
            try:
                await publish_ocr_completed(out_event)
            except Exception as e:
                print("[OCRConsumer] publish failed:", e)

    finally:
        await close_consumer(consumer)
