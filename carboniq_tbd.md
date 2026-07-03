# CarbonIQ (TBD)

---

# 📄 MVP Specification: **CarbonIQ – Scope 2 Emissions Module (v1.0)**

### **Updated Scope:**

Focus exclusively on **automated Scope 2 carbon accounting** and **offset attribution**, including:

- Hourly energy mix estimation
- Emissions factor calculation
- Matching with RECs, PPAs, and offsets
- Bill-to-kWh inference
- At least **95% estimation accuracy**

---

## 🧭 1. Product Vision

CarbonIQ is an AI-powered platform that simplifies **Scope 2 emissions reporting** for Australian SMEs and their advisors. It automatically ingests energy data (from bills, meters, or APIs), estimates time-matched emissions using grid mix data, and reconciles this with verified renewable energy purchases (RECs, PPAs, GreenPower). Outputs are **audit-ready** for Climate Active and **ASRS-aligned**.

---

## ⚙️ 2. Core MVP Features (Scope 2 Only)

### 🔹 A. Energy Data Ingestion & Normalization

| Source | Input Method | Details |
| --- | --- | --- |
| **Smart meter (NMI)** | CSV upload, API | Half-hourly or 15-min interval data |
| **Energy bills** | OCR upload, manual | Extrapolate total kWh and month |
| **GreenPower / PPA contracts** | Manual input + registry match | Metadata + volume by period |
| **REC certificate IDs** | Upload or lookup | To track matching eligibility |

---

### 🔹 B. Grid Emissions Estimation Engine

- **Grid mix data**: Hourly generation profile by fuel type (via AEMO or OpenNEM)
- **Emission factors**:
    - Per fuel source (coal, gas, solar, wind, hydro)
    - Location-based (e.g., NSW, SA, QLD)
- **Estimation logic**:
    - Convert kWh into CO₂e using dynamic hourly intensity
    - Assign source breakdown (e.g., 23% solar, 44% coal)
- **Backcasting option** for non-interval data (using month avg)

---

### 🔹 C. Emissions Attribution & Offset Matching

- **Matching logic**:
    - Step 1: Confirm consumption (from bill or meter)
    - Step 2: Calculate hourly emissions (grid-mix x kWh)
    - Step 3: Attribute eligible renewables:
        - **Metered onsite solar (if available)**
        - **GreenPower purchases**
        - **RECs / LGCs**
        - **Corporate PPA volume**
    - Step 4: Show **residual emissions** (what needs to be offset)
- **Output**: Hourly “matching score” (like EnergyTag), % of renewable attribution

---

### 🔹 D. Output & Reporting

- **Audit-ready exports**:
    - Scope 2 report (location-based and market-based)
    - Emissions breakdown by source
    - Offset mapping and attribution
    - Climate Active-ready disclosures (simplified)
- **File formats**: PDF, CSV, Climate Active templates

---

### 🔹 E. Accuracy Control & AI Enhancements

- Bill-kWh inference:
    - Use NLP/OCR to extract billing periods and total usage
    - Compare with industry benchmarks and local climate
    - If only $ cost is known, use tariff lookup + regression
- AI Estimator:
    - When interval data is missing, infer load profile using:
        - Business type
        - Operating hours
        - Weather metadata
    - **Accuracy threshold**: ≥95% compared to known intervals (calibration benchmark)

---

## 🧠 3. AI Capabilities (MVP Level)

| Function | Method |
| --- | --- |
| OCR & NLP | Extracts meter numbers, periods, kWh, cost from bills |
| AI agent | Explains results, answers queries like "Why is my emission high in June?" |
| Forecasting | Not in MVP — optional in v2 |

---

## 📊 4. Outputs

### 🔸 Example Dashboard:

- Total Scope 2 Emissions (tCO₂e)
- % Matched by Renewables
- Breakdown by:
    - Grid electricity
    - GreenPower
    - Onsite solar
    - Unmatched (to be offset)

### 🔸 Exported Report:

- Total consumption
- Hourly emissions (or month-average fallback)
- Offset summary (matched vs residual)
- Climate Active-aligned Scope 2 summary

---

## ⚙️ 5. Back-End Infrastructure

| Layer | Tech |
| --- | --- |
| **Frontend** | React + Tailwind |
| **Backend** | Python (FastAPI), PostgreSQL |
| **AI** | OpenAI GPT-4 API, LangChain (chat agent), Tesseract for OCR |
| **Data Feeds** | AEMO, OpenNEM, Climate Active Registry, NGAF (DCCEEW) |

---

## 🚧 6. Out of Scope (For Later Versions)

- Scope 1 or Scope 3 emissions
- Offset purchasing
- Full Climate Active certification process
- Blockchain audit trail
- Consultant dashboard

---

## ✅ 7. Success Metrics

| Metric | Target |
| --- | --- |
| kWh to CO₂e conversion accuracy | ≥95% |
| Time to report (from bill upload) | < 10 minutes |
| User satisfaction | ≥8/10 |
| % automated data processing | ≥90% of inputs |

---

## 📍 8. MVP User Flow

1. **User signs up**
2. **Uploads energy bill or meter file**
3. **Selects location + business type**
4. **System estimates hourly emissions**
5. **User uploads RECs or GreenPower metadata**
6. **Matching engine computes offset coverage**
7. **Report is generated**
