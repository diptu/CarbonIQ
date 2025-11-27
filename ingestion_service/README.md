# Ingestion Service

The **Ingestion Service** is a lightweight, async-first microservice responsible for handling file uploads and retrieving metadata.
This version includes **FastAPI BackgroundTasks**, ensuring that time-consuming operations (DB writes, Redis publishing, hashing, preprocessing, etc.) run **asynchronously in the background** without delaying API responses.

Ideal for:
- ETL pipelines
- OCR / ML preprocessing
- Analytics ingestion
- Multi-tenant SaaS upload workflows

---

## 🚀 Features

### **POST /upload**
- Accepts any file: PDF, CSV, images, videos, etc.
- Saves file to disk (`./uploads/` by default).
- Immediately returns a `file_id` while processing continues in the **background task**.
- Background task performs:
  - Metadata extraction
  - DB save
  - Redis cache entry
  - Publish job to queue (`ingest:queue`)

### **GET /uploads/{file_id}**
- Fetch metadata from Redis (fast)
- Falls back to DB storage if not cached

---
