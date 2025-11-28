# 📄 OCR Service

The **OCR Service** is a lightweight, event-driven microservice responsible for extracting **energy consumption data** from uploaded utility bills and publishing the results for downstream processing.

This service consumes file metadata from **Kafka**, performs OCR on the referenced files (local/S3), stores the extracted fields in a database, and publishes normalized OCR output as an event for the **Normalization Service**.

Designed for:

- Energy & carbon accounting pipelines
- Bill/invoice data extraction
- ETL/ELT async data workflows
- Microservice and event-driven architectures

---

## 🚀 Features

### **🎧 Kafka Consumer — `ingestion.file.ready`**

Triggered after the Ingestion Service saves a file.

- Receives:
  - `file_id`
  - `tenant_id`
  - `storage_path` or `s3_uri`
  - metadata (size, mime-type, timestamps)

- Automatically runs OCR:
  - PDF text extraction
  - Image OCR (if applicable)
  - Field detection (kWh, meter ID, billing period)
  - Basic heuristics for utility bill formats

- Saves extracted OCR results into PostgreSQL.

- Publishes event:
  **`ocr.raw.extracted`**

---

### 📨 Event Produced — `ocr.raw.extracted`

Once OCR extraction completes, the service publishes a JSON payload like:

```json
{
  "file_id": "45be9c0a-aa23-4e74-a817-0b76575a9088",
  "tenant_id": "tenant_123",
  "ocr_text": "... full extracted text ...",
  "raw_fields": {
    "meter_id": "1234567",
    "kwh": "920.4 kWh",
    "billing_period": "01 Jul 2024 - 31 Jul 2024"
  },
  "source_path": "/data/uploads/x.pdf"
}
```

This event is consumed by the Normalization Service.
### 🗂 Storage

The service stores extracted fields into:

PostgreSQL

  - OCR results table

  - inked to file_id

(Optional) Redis

  - Caching extracted text

  - Avoid recomputation

### 🧩 REST API (Optional)

  - Although event-driven, the service also exposes a simple API (useful for debugging and QA):

  - GET /ocr/{file_id}

      - Fetch OCR results by file_id.

Example response:

```json
{
  "file_id": "45be9c0a-aa23-4e74-a817-0b76575a9088",
  "raw_text": "...",
  "fields": {
    "kwh": "920.4 kWh",
    "meter_id": "1234567",
    "billing_period": "01 Jul 2024 - 31 Jul 2024"
  },
  "created_at": "2025-01-02T10:22:10Z"
}

```
Example of ingestion event (what ingestion service must produce)

```json
{
  "file_id": "invoice-0001",
  "tenant_id": "tenant_1",
  "org_id": "org_1",
  "local_path": "/data/uploads/invoice-0001.pdf",
  "s3_key": null
}

```
### 🏗️ Architecture Overview

```css
 ┌───────────────────────┐
 │   Ingestion Service   │
 │  (file saved + meta)  │
 └──────────┬────────────┘
            │ Kafka: ingestion.file.ready
            ▼
 ┌───────────────────────┐
 │      OCR Service      │
 │  - extract text        │
 │  - detect kWh, dates   │
 │  - save to DB          │
 │  - emit OCR event      │
 └──────────┬────────────┘
            │ Kafka: ocr.raw.extracted
            ▼
 ┌──────────────────────────┐
 │   Normalization Service   │
 │   (kWh → float, dates)    │
 └──────────────────────────┘

```
### 🧪 End-to-End Flow

  - User uploads file → Ingestion Service

  - File saved → event published:
  ingestion.file.ready

  - OCR Service consumes it, runs OCR

  - OCR results saved → event published:
  ocr.raw.extracted

  - Normalization Service consumes event and normalizes fields

  - Calculation Service computes carbon emissions
