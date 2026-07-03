# CarbonIQ — Public Datasets for User Journey Evaluation

**Version:** 1.0
**Date:** 2026-07-03
**Purpose:** Map each user persona to free, public datasets that can be used to test, calibrate, and validate their end-to-end journey on CarbonIQ.

---

## 📋 Table of Contents

1. [Quick Reference Matrix](#-quick-reference-matrix)
2. [Per-Persona Evaluation Datasets](#-per-persona-evaluation-datasets)
3. [Shared Cross-Journey Datasets](#-shared-cross-journey-datasets)
4. [Evaluation Test Recipes](#-evaluation-test-recipes)
5. [Data Gaps & Workarounds](#-data-gaps--workarounds)

---

## 🎯 Quick Reference Matrix

| Dataset | Format | Coverage | Best For | Persona(s) | Link |
|---------|--------|----------|----------|------------|------|
| **OpenNEM / OpenElectricity API** | JSON/CSV API | NEM + WEM, 30-min | Grid emissions calc | 1, 2, 3, 4, 5, 8 | https://docs.openelectricity.org.au |
| **AEMO WEM Market Data** | CSV | WEM 2012→now | WA-specific validation | 1, 2, 5, 8 | http://data.wa.aemo.com.au |
| **NGA Factors 2025 (DCCEEW)** | XLSX/PDF | National, by state | Emission factors | All except 6, 9, 10 | https://www.dcceew.gov.au/climate-change/publications/national-greenhouse-accounts-factors-2025 |
| **Smart-Grid Smart-City Trial** | CSV (7zipped, 16GB) | NSW households, half-hourly | Interval data ingestion | 1, 2, 8 | https://www.data.gov.au/data/dataset/smart-grid-smart-city-customer-trial-data |
| **NEM12 Sample Files** | CSV (zipped) | NEM-wide | NEM12 parser test | 1, 2, 8 | https://github.com/charliedotau/Smart-Meter-File-Format-Examples-Aus |
| **APVI Solar Maps API** | JSON API | National, 2-digit postcode | Solar/onsite estimation | 1, 2, 8 | https://pv-map.apvi.org.au |
| **CER LGC Registry & REGO** | CSV/XLSX + Public Register | National | REC matching, registry lookup | 1, 2, 3, 5, 10 | https://cer.gov.au/markets/reports-and-data/large-scale-renewable-energy-data |
| **Climate Active Disclosure Examples** | PDF | Various | Report template validation | 1, 2, 3, 5, 10 | https://www.climateactive.org.au |
| **AER CDR Product Reference Data** | JSON API | NSW/QLD/SA/VIC/TAS/ACT | Tariff lookup, kWh inference | 1, 2, 3, 8 | https://www.aer.gov.au/energy-product-reference-data |
| **ERA WA Retailer Dashboards** | Web/CSV | WA, 2014→ | WA-specific consumption | 1, 2, 3, 5 | https://www.erawa.com.au/energyreports |
| **CSIRO NEAR Zone Substation Data** | CSV | WA (Western Power, Horizon Power) | Half-hourly load profiles | 1, 2, 5, 8 | https://near.csiro.au/assets/ |
| **Australian Energy Statistics (DCCEEW)** | XLSX | National, annual | Historical context | 2, 3, 7, 8 | https://www.energy.gov.au/energy-data/australian-energy-statistics |
| **ACCC NEM Inquiry 2024** | PDF + underlying CSV | NEM-wide | Tariff benchmarking | 3, 7 | https://www.accc.gov.au/system/files/accc-national-electricity-market-december-2024-report.pdf |
| **Energy Consumers Australia SME Tariff Tracker** | XLSX | National SME | SME benchmark kWh | 2, 3, 8 | https://energyconsumersaustralia.com.au/projects/retail-tariff-tracker |
| **Mendeley SGSC Clustered Load Profiles** | CSV | NSW, 6,031 households | Cluster templates, AI training | 8 | https://data.mendeley.com/datasets/zm4f727vvr/1 |
| **Low Carbon London (UK)** | CSV (~167M rows) | UK, 5,567 households | Smart meter UX benchmarks | 8 (compare) | https://data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d |
| **Ausgrid Solar Home Data** | CSV | NSW, 300 homes | Solar export analysis | 1, 2 | https://www.ausgrid.com.au/Industry/Our-Research/Data-to-share/Solar-home-electricity-data |
| **CSIRO Data Access Portal** | Various | National | Datasets discovery | 8 | https://data.csiro.au/ |
| **AEMO Rooftop PV (ASEFS)** | CSV | NEM regions | Distributed solar estimates | 2, 5, 8 | https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/nem-forecasting-and-planning/operational-forecasting/solar-and-wind-energy-forecasting/australian-solar-energy-forecasting-system |

---

## 👥 Per-Persona Evaluation Datasets

### 1. SME Owner / Operator

**Journey to test:** Sign up → Upload bills/smart meter → View emissions → Export Climate Active PDF

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Sign up + create org | None (use synthetic) | Org model, NMI storage |
| Upload energy bill (OCR) | **Sample bill images** (need to source — see gap section) | OCR accuracy, NMI extraction, kWh extraction |
| Upload NEM12 smart meter | **Smart-Grid Smart-City data** or **NEM12 sample files** | Parser correctness, interval ingestion |
| Match location to grid | **OpenNEM API** | Correct region resolution (NSW1, VIC1, etc.) |
| Compute hourly emissions | **OpenNEM** × uploaded kWh | Emission factor applied correctly |
| View source breakdown | **OpenNEM generation mix** | Mix percentages shown match upstream |
| Upload GreenPower | **CER LGC public register** | REC ID lookup, registry match |
| Upload onsite solar | **APVI Solar Maps API** | Estimated generation matches location |
| Export PDF/CSV | **Climate Active disclosure template** | Output format matches required structure |
| Run AI query | Synthetic question corpus | LLM context retrieval, answer quality |

**Key public datasets:**
- 🥇 https://docs.openelectricity.org.au — primary emissions calculation engine
- 🥇 https://www.data.gov.au/data/dataset/smart-grid-smart-city-customer-trial-data — 16GB real Australian smart meter data (free)
- 🥇 https://github.com/charliedotau/Smart-Meter-File-Format-Examples-Aus — NEM12 file samples from real retailers
- 🥇 https://www.dcceew.gov.au/climate-change/publications/national-greenhouse-accounts-factors-2025 — emission factors
- 🥇 https://pv-map.apvi.org.au — solar generation estimates by postcode
- 🥇 https://www.climateactive.org.au — disclosure templates for export validation

---

### 2. SME Sustainability / ESG Manager

**Journey to test:** Multi-site org → Quarterly bulk upload → Cross-site reporting → API integration

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Multi-site setup | Synthetic org with 4 sites | Multi-tenancy model |
| Bulk upload (4 sites) | **Smart-Grid Smart-City** (subset) × 4 regions | Parallel processing |
| Historical backfilling | **ERA WA dashboards** or **Australian Energy Statistics** | Multi-year continuity |
| Cross-site rollup | Aggregate across 4 sites | Reporting math correctness |
| Per-site renewable attribution | **CER LGC registry** + **APVI** | Per-site market-based Scope 2 |
| AI: highest intensity site | **AEMO ASEFS** (rooftop PV) + **OpenNEM** | Per-region intensity variation |
| API/webhook delivery | **OpenNEM API** style | Real-time push working |
| Climate Active submission | **Climate Active disclosure templates** (NAB, AWS, etc.) | Format compliance |

**Key public datasets:**
- 🥇 https://near.csiro.au/assets/a0f615ec-d3d3-4e24-970a-72548effc060 — Western Power zone substation (30-min, multi-year)
- 🥇 https://near.csiro.au/assets/a08f3824-f2b1-47b0-965a-c2fb928c72bb — Horizon Power zone substation (30-min, regional WA)
- 🥇 https://www.energy.gov.au/energy-data/australian-energy-statistics — annual multi-year context
- 🥇 https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/nem-forecasting-and-planning/operational-forecasting/solar-and-wind-energy-forecasting/australian-solar-energy-forecasting-system — distributed PV by region
- 🥇 https://www.climateactive.org.au — multiple real-world disclosures to study

---

### 3. Energy Advisor / Sustainability Consultant

**Journey to test:** Manage 25 client orgs → Bulk operations → Portfolio rollup → White-label reports

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Multi-tenant advisor | Synthetic 25 orgs | Advisor → org mapping |
| Bulk data collection | **25x subsets of SGSC data** | Bulk import latency, error handling |
| Portfolio calculation | Aggregated across 25 | Math, performance |
| White-label export | **NAB Climate Active disclosure** as template | PDF branding applied correctly |
| Portfolio analytics | Aggregated emissions | Rollup correctness |
| Bulk client comms | Synthetic emails | Email template, scheduling |

**Key public datasets:**
- 🥇 https://energyconsumersaustralia.com.au/projects/retail-tariff-tracker — SME benchmark data (consumption patterns)
- 🥇 https://www.erawa.com.au/energyreports — WA retailer data 2014→ (synthetic client data)
- 🥇 https://www.billzap.com.au/market-rates.php — current retailer benchmarks by state
- 🥇 https://www.accc.gov.au/system/files/accc-national-electricity-market-december-2024-report.pdf — NEM pricing study
- 🥇 https://www.climateactive.org.au — multiple disclosure examples for white-label templates

---

### 4. Accountant / Bookkeeper

**Journey to test:** Read-only access → Pull Scope 2 data → Cross-reference with financials

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Invitation flow | Synthetic email | RBAC enforcement |
| Read-only dashboard | **OpenNEM** × synthetic org | Read-only scope enforced |
| Export CSV | Synthetic org emissions | CSV schema compatible with Xero/MYOB |
| Cross-ref with financials | **Australian Energy Statistics** | Same kWh source-of-truth |
| Anomaly detection | Synthetic orgs | Edge case flagging |

**Key public datasets:**
- 🥇 https://www.energy.gov.au/energy-data/australian-energy-statistics — historical baseline for cross-checks
- 🥇 https://docs.openelectricity.org.au — verified emissions source for read-only API
- 🥇 https://www.aer.gov.au/retail-markets/guidelines-reviews/electricity-and-gas-consumption-benchmarks-for-residential-customers-2020 — AER consumption benchmarks

---

### 5. External Auditor

**Journey to test:** Access locked report → Verify calculations → Cross-check source data → Sign off

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Access link expiry | None (synthetic) | Time-limited, MFA-gated |
| View locked report | Synthetic org with lock | Report immutable post-lock |
| Verify calculations | **OpenNEM + NGA Factors** (independent recompute) | Match within 0.1% |
| Cross-check bill kWh | **Synthetic bill vs SGSC total** | kWh reconciliation |
| Verify REC IDs | **CER LGC public register** (https://www.rec-registry.gov.au/rec-registry/app/public/lgc-register) | Real certificate lookup |
| Verify emission factors | **NGA Factors** | Year-of-data factor used |
| Sign-off | None | Audit log entry created |

**Key public datasets:**
- 🥇 https://www.dcceew.gov.au/climate-change/publications/national-greenhouse-accounts-factors-2025 — authoritative factor lookup
- 🥇 https://docs.openelectricity.org.au — recompute emissions independently
- 🥇 https://www.rec-registry.gov.au/rec-registry/app/public/lgc-register — public LGC registry
- 🥇 https://www.climateactive.org.au/sites/default/files/2024-08/technical_guidance_manual_2024.pdf — technical guidance manual

---

### 6. Customer Support / Success

**Journey to test:** Diagnose ticket → View user data → Impersonate → Re-run calculation

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| View user account | Synthetic user | Scoped access only |
| Inspect ingestion logs | Synthetic failures | Error categorization |
| OCR failure diagnosis | **SGSC data** with corrupted entries | OCR confidence threshold |
| Impersonation | Synthetic user | Audit log created |
| Re-run calculation | Synthetic org + **OpenNEM** | Calculation re-run |
| Tag ticket | Synthetic | Internal tagging works |

**Key public datasets:**
- 🥇 https://data.mendeley.com/datasets/zm4f727vvr/1 — pre-clustered load profiles (clean + dirty data examples)
- 🥇 https://www.data.gov.au/data/dataset/smart-grid-smart-city-customer-trial-data — full ingestion history incl. failures
- Use synthetic OCR failures generated by corrupting these

---

### 7. Platform Admin (Super Admin)

**Journey to test:** Daily health → User mgmt → Feature flags → Incident response → Billing

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Active user dashboard | Synthetic admin view | Aggregations correct |
| Suspend non-paying | Synthetic | Action logged |
| Feature flag rollout | Synthetic | Toggle works for 50 orgs |
| Incident response | **OpenNEM status** monitoring | Alert when stale |
| Emission factor update | **NGA Factors 2025** | Re-trigger calculations |
| Failed payment list | Synthetic billing data | Dunning workflow |

**Key public datasets:**
- 🥇 https://www.energy.gov.au/energy-data/australian-energy-statistics — for admin reporting rollups
- 🥇 https://cer.gov.au/markets/reports-and-data/large-scale-renewable-energy-data — for renewable energy portfolio stats
- 🥇 https://docs.openelectricity.org.au — for system status dashboard

---

### 8. Data / ML Operations

**Journey to test:** Monitor model accuracy → Detect drift → Retrain → Refresh emission factors

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Accuracy benchmark | **SGSC** ground-truth intervals vs predicted | ≥95% threshold met |
| Drift detection | **SGSC** × 30 days | Statistical drift alerts |
| OCR retraining | Synthetic + **SGSC customer data** | New model performance |
| Emission factor refresh | **NGA Factors 2025** | Background recalc works |
| AEMO feed health | **OpenNEM** API monitor | Stale-data detection |
| A/B test new model | **SGSC half** vs **SGSC half** | Statistical significance |

**Key public datasets:**
- 🥇 https://data.mendeley.com/datasets/zm4f727vvr/1 — 6,031 clustered household profiles (2013, NSW)
- 🥇 https://www.data.gov.au/data/dataset/smart-grid-smart-city-customer-trial-data — raw 11.6GB customer trial data
- 🥇 https://docs.openelectricity.org.au — for comparing AEMO emissions
- 🥇 https://www.dcceew.gov.au/climate-change/publications/national-greenhouse-accounts-factors-2025 — factor refresh
- 🥇 https://www.kaggle.com/datasets/ziya07/smart-meter-electricity-consumption-dataset — supplementary international test data
- 🥇 https://www.low-carbon-london-data — UK benchmark for sanity-checking your model against global results
- 🥇 https://www.energy.gov.au/energy-data/australian-energy-statistics — historical Australian total energy

---

### 9. API / Integration User (Machine-to-Machine)

**Journey to test:** API key generation → Auth → Pull data → Webhook delivery

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Generate API key | Synthetic | Key returned, scoped permissions |
| Authenticate | Synthetic | Bearer token validated |
| Pull emissions | **OpenNEM** × synthetic org | JSON schema stable |
| Webhook on event | Synthetic | POST to webhook URL works |
| Rate limit handling | Synthetic burst | 429 returned correctly |
| Revoke key | Synthetic | Immediate effect |

**Key public datasets:**
- 🥇 https://docs.openelectricity.org.au/introduction — reference API design (well-documented open API to model against)
- 🥇 https://www.aer.gov.au/energy-product-reference-data — public CDR-style API with no accreditation
- Synthetic org data for endpoint testing

---

### 10. Regulator / Climate Active Reviewer

**Journey to test:** Receive submission → Access verification link → Review locked report → Verify outcome

**Datasets needed:**

| Test Step | Dataset | What to Validate |
|-----------|---------|------------------|
| Receive submission | Synthetic link | Link generation correct |
| Access gating | Synthetic | MFA + scope enforced |
| Review locked report | Synthetic org | Immutable view |
| Methodology check | **NGA Factors** | Factor version correct |
| Approve / Reject | Synthetic | Audit log created |
| Link expiry | None | 60-day expiry |

**Key public datasets:**
- 🥇 https://www.climateactive.org.au — real Climate Active disclosure statements (NAB, AWS, City of Melbourne, Charles Sturt Uni)
- 🥇 https://www.climateactive.org.au/sites/default/files/2024-08/technical_guidance_manual_2024.pdf — technical guidance
- 🥇 https://standards.aasb.gov.au/sites/default/files/2024-10/AASBS2_09-24.pdf — AASB S2 standard
- 🥇 https://www.ifrs.org/content/dam/ifrs/publications/html-standards-issb/english/2023/issued/issbs2-ag.html — IFRS S2 illustrative guidance
- 🥇 https://ghgprotocol.org/sites/default/files/2023-03/Scope%202%20Guidance.pdf — GHG Protocol Scope 2 standard

---

## 🔄 Shared Cross-Journey Datasets

These power the **core engine** that every persona benefits from:

### 1. Grid Emissions Calculation (the heart of CarbonIQ)

**Primary: Open Electricity (formerly OpenNEM)**
- 🔗 https://docs.openelectricity.org.au/introduction
- API: https://api.openelectricity.org.au/v3/
- License: MIT (code), CC BY-NC 4.0 (data)
- Returns: per-region hourly emissions (tCO2e), intensity (kgCO2e/MWh), generation by fuel
- Coverage: NEM (NSW/QLD/SA/VIC/TAS) + WEM (WA) + APVI rooftop + BoM weather

**Backup: AEMO WEM Data**
- 🔗 http://data.wa.aemo.com.au
- License: Open (per AEMO terms)
- Returns: 30-min trading/dispatch intervals for WA SWIS

**Backup: Ember Energy**
- 🔗 https://ember-energy.org/data/electricity-data-explorer/
- License: Open
- Returns: global + Australian monthly generation/emissions

---

### 2. Emission Factors

**Primary: DCCEEW NGA Factors 2025**
- 🔗 https://www.dcceew.gov.au/climate-change/publications/national-greenhouse-accounts-factors-2025
- Format: XLSX (93 KB), PDF (1.2 MB), DOCX (783 KB)
- License: CC BY 4.0
- Contains: Scope 1/2/3 factors by state and fuel type
- Update: Annually (current = 2025 edition for 2025-26 reporting)

**Why primary:** It's what NGER reporters are legally required to use and what ASRS reporters default to. If you use anything else, you need to justify why.

---

### 3. Smart Meter / Half-Hourly Data

**Primary: Smart-Grid Smart-City Customer Trial**
- 🔗 https://www.data.gov.au/data/dataset/smart-grid-smart-city-customer-trial-data
- License: CC BY 3.0 AU
- Size: 16GB uncompressed (7zipped)
- Contains: 12,000+ NSW households, half-hourly intervals, 2010-2014
- Linked: appliance, demographic, tariff data

**Primary (cleaned): Mendeley clustered profiles**
- 🔗 https://data.mendeley.com/datasets/zm4f727vvr/1
- 6,031 NSW households, 2013, already cleaned and clustered

**Primary (WA-specific): CSIRO NEAR**
- 🔗 https://near.csiro.au/assets/
- Western Power: 2007-2016, 30-min, zone substation level
- Horizon Power: 2013-2015, 30-min, zone substation level

**Primary (NEM12 spec): AEMO MDFF Spec + samples**
- 🔗 https://www.aemo.com.au/-/media/files/electricity/nem/retail_and_metering/market_settlement_and_transfer_solutions/2024/mdff-specification-nem12-nem13-v26-clean-final.pdf
- Sample files: https://github.com/charliedotau/Smart-Meter-File-Format-Examples-Aus
- Real NEM12 files from AusNet, AGL, etc.

---

### 4. RECs / LGCs / GreenPower

**Primary: CER Public Registers**
- 🔗 https://www.rec-registry.gov.au/rec-registry/app/public/lgc-register
- 🔗 https://cer.gov.au/markets/reports-and-data/large-scale-renewable-energy-data
- Format: Web UI + CSV downloads
- License: Open

**Use case:** Match user-uploaded REC IDs against public registry; verify GreenPower claims

---

### 5. Solar Generation (Onsite Estimation)

**Primary: APVI Solar Maps**
- 🔗 https://pv-map.apvi.org.au/live
- API: https://pv-map.apvi.org.au/api/v2/2-digit/{date}.json
- Returns: 15-min PV performance + estimated generation by 2-digit postcode region

**Secondary: AEMO ASEFS**
- 🔗 https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/nem-forecasting-and-planning/operational-forecasting/solar-and-wind-energy-forecasting/australian-solar-energy-forecasting-system
- Returns: 30-min rooftop PV estimates by NEM region

---

### 6. Tariff / Pricing (for bill-to-kWh inference)

**Primary: AER Energy Product Reference Data (CDR)**
- 🔗 https://www.aer.gov.au/energy-product-reference-data
- API: Public, no accreditation
- Coverage: NSW, QLD, SA, VIC, TAS, ACT
- Returns: every published retail plan with rates, supply charges, FiT

**Secondary: AER Residential Consumption Benchmarks**
- 🔗 https://www.aer.gov.au/retail-markets/guidelines-reviews/electricity-and-gas-consumption-benchmarks-for-residential-customers-2020
- Returns: annual kWh benchmarks by state and segment

---

### 7. WA-Specific (SWIS)

**Primary: AEMO WEM Data** — already listed
**Primary: ERA WA Reports**
- 🔗 https://www.erawa.com.au/energyreports
- Returns: licensee data since 2014 (GWh delivered, customer accounts, gas TJ)
- License: Open

**Primary: WA Government Open Data**
- 🔗 https://catalogue.data.wa.gov.au/
- Search: energy, electricity

---

## 🧪 Evaluation Test Recipes

### Recipe 1: Validate OCR accuracy on energy bills
```
1. Take 50 sample energy bills (PDF/image)
2. Run through your OCR pipeline
3. Compare extracted fields (kWh, NMI, period, $) against ground truth
4. Target: ≥95% accuracy on kWh extraction, ≥99% on NMI
```

### Recipe 2: Validate emissions calculation
```
1. Take a known site (e.g., SGSC household 12345)
2. Pull their half-hourly interval data
3. Multiply each interval by OpenNEM's region intensity
4. Sum to get total tCO2e
5. Compare to CarbonIQ's output for the same input
6. Target: <1% deviation
```

### Recipe 3: Validate kWh-to-emissions "≥95% accuracy"
```
1. Take interval data from SGSC (ground truth)
2. Down-sample to monthly aggregates (simulating "bill-only" input)
3. Use OpenNEM monthly intensity to compute emissions
4. Compare to ground-truth hourly emissions
5. Target: ≥95% accuracy on monthly emissions
```

### Recipe 4: Validate REC matching
```
1. Generate 10 synthetic REC IDs (or use real ones from CER public register)
2. Upload to CarbonIQ
3. Verify system queries CER registry
4. Verify eligibility period matching (REC vintage vs consumption period)
5. Verify double-counting prevention
```

### Recipe 5: Validate Climate Active template export
```
1. Generate report for a synthetic org
2. Compare to Climate Active disclosure template format
3. Required fields per template:
   - Scope 2 location-based (tCO2e)
   - Scope 2 market-based (tCO2e)
   - Methodology disclosure
   - Energy attribute purchases
   - Offset summary
4. Target: passes Climate Active technical guidance manual checks
```

### Recipe 6: Validate advisor portfolio rollup
```
1. Create 5 synthetic orgs with different consumption profiles
2. Calculate emissions per org
3. Roll up to portfolio total
4. Compare portfolio total to manual sum
5. Target: 100% math accuracy
```

---

## ⚠️ Data Gaps & Workarounds

### Gap 1: No public dataset of sample Australian energy bills (PDFs)
**Why it matters:** Your OCR engine needs test images.

**Workarounds:**
1. **Generate synthetic bills** using a template renderer (faker + reportlab)
2. **Scrape with permission** — most retailer websites have sample bill images for download
3. **Manually collect** redacted bills from test users (with consent)
4. **Use the Mendeley clustered dataset docs** as text-only OCR fallback
5. **Australian-specific dataset:** Search Kaggle for "Australian electricity bill" — limited but some exist

**Suggested:** Build a synthetic bill generator that produces variations:
- Different retailers (AGL, Origin, EnergyAustralia, AGL, Red Energy)
- Different formats (single rate, time-of-use, demand)
- Different quality (300dpi scan, photo, fax)
- Different layouts (1-page, multi-page)

### Gap 2: No public household-level WA smart meter data
**Why it matters:** You're WA-focused but the canonical smart meter dataset is NSW.

**Workarounds:**
1. Use **CSIRO NEAR zone substation data** (WA-specific, 30-min, ~2 years)
2. Use **SGSC** as proxy, document the geographic caveat
3. **Apply to Western Power directly** as a research partner (mentioned in their 2020 information sheet)
4. Use **synthetic data** generated from NSW profiles × WA-specific temperature/business-mix adjustments

### Gap 3: No public "GreenPower" certificate registry
**Why it matters:** Need to verify GreenPower claims.

**Workarounds:**
1. **CER LGC registry** covers voluntary surrenders (GreenPower is voluntary surrender)
2. Build a "claimed GreenPower" registry from retailer disclosure pages
3. Trust user input with audit trail (most realistic for MVP)

### Gap 4: No public Climate Active submission API
**Why it matters:** You want to push directly to Climate Active.

**Workarounds:**
1. Generate **PDF in their exact format** (study published disclosures)
2. Manual submission by user (per Climate Active process)
3. No public API — this is a hard gap, not a workaround problem

### Gap 5: No public commercial real estate electricity data
**Why it matters:** SME market is dominated by offices/retail, but most public data is residential.

**Workarounds:**
1. **Use NSW DNSP zone substation data** (CSIRO NEAR) for SMB load profiles by area
2. **Use SGSC** with caveat that it's residential
3. **Apply to individual DNSPs** for commercial data (some publish aggregated)
4. **Use ABS Commercial Building data** + energy benchmarks from ECA SME Tracker

### Gap 6: Limited public tariff data for WA
**Why it matters:** WA sits outside NEM CDR.

**Workarounds:**
1. **ERA WA** publishes regulated prices annually
2. **WATTever** publishes WA retailer rates (https://wattever.com.au/compare-electricity-prices/)
3. **Energy Policy WA** (https://www.energy.wa.gov.au) for the official source
4. **Bill Zap** (https://www.billzap.com.au/market-rates.php) — has WA plans
5. Scrape Synergy / Horizon Power / Alinta WA pages quarterly

### Gap 7: Limited WEM historical data before 2012
**Why it matters:** Multi-year reporting.

**Workarounds:**
1. Use **ERA reports** for pre-2012 data (synthetic on licensee level)
2. Backcasting using **NGA Factors** (location-based methodology works backward)

---

## 📊 Suggested Evaluation Datasets by Priority

If you only have time to integrate 5 datasets, start with these:

| # | Dataset | Why | Effort |
|---|---------|-----|--------|
| 1 | **OpenNEM API** | Core engine for emissions calculation | Low (REST API) |
| 2 | **NGA Factors 2025** | Authoritative emission factors | Low (download XLSX) |
| 3 | **Smart-Grid Smart-City** | Test data for half-hourly ingestion | Medium (16GB download) |
| 4 | **CER LGC Public Register** | REC matching | Low (web UI + CSV) |
| 5 | **AER CDR API** | Tariff lookup for bill inference | Low (public API) |

Then add (in priority order):
6. **APVI Solar Maps API** — for onsite solar estimation
7. **ERA WA Reports** — for WA-specific validation
8. **CSIRO NEAR Zone Substation** — for WA load profiles
9. **Climate Active Disclosures** — for export format validation
10. **AEMO WEM Data** — for WA grid mix

---

## 🔗 Useful Aggregator Links

- **DITRDCSA Data Catalogue** — https://catalogue.data.infrastructure.gov.au/dataset/ — search all Australian gov datasets
- **Data.gov.au** — https://data.gov.au — federal open data
- **Data WA** — https://catalogue.data.wa.gov.au — WA government open data
- **data.nsw.gov.au** — https://data.nsw.gov.au — NSW
- **AEMO Data** — https://www.aemo.com.au/energy-systems — electricity market data
- **CSIRO Data Access Portal** — https://data.csiro.au/ — research datasets
- **ARENA Knowledge Bank** — https://arena.gov.au/knowledge-bank — energy research reports

---

## 📝 License Compatibility Notes

| Dataset | License | Commercial Use OK? | Attribution Required? |
|---------|---------|--------------------|-----------------------|
| OpenNEM / OpenElectricity | MIT (code), CC BY-NC 4.0 (data) | ⚠️ Non-commercial only | Yes |
| AEMO WEM | Open per AEMO terms | ✅ Yes | Yes |
| DCCEEW NGA Factors | CC BY 4.0 | ✅ Yes | Yes |
| SGSC | CC BY 3.0 AU | ✅ Yes | Yes |
| CER data | Open Government | ✅ Yes | Yes |
| APVI | Open | ✅ Yes | Yes |
| AER CDR | Open | ✅ Yes | Yes |
| Mendeley | CC BY 4.0 | ✅ Yes | Yes |

**⚠️ Important:** OpenNEM is CC BY-NC 4.0 (non-commercial). If you're building a commercial product:
- Use **AEMO data directly** (which OpenNEM mirrors, but AEMO allows commercial use)
- Or **contact OpenElectricity** about commercial licensing
- Their API platform (https://platform.openelectricity.org.au) is a commercial product

---

**End of document**