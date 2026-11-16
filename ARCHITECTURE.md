# Veloxa CXO Cockpit - Architecture & System Design
**Author:** Riddhi Dey  
**Date:** Monday, 16 November 2026 (Day 1)  
**Version:** 1.0.0  

---

## 1. Executive Summary & Objective

The **Veloxa CXO Cockpit** is an executive intelligence and decision-support system designed for **Ananya Rao**, CEO of Veloxa Technologies. 

Rather than presenting static BI charts and vanity dashboards, the cockpit delivers:
1. **Evidence-Grounded Executive Q&A:** Fast, concise answers to operational, financial, and strategic questions, with mandatory citations to primary records.
2. **Explicit Uncertainty & Conflict Refusal:** Principled handling of contradictory data (e.g. leadership call statements vs. GL/HRMS exports), admitting uncertainty or flagging disagreements instead of guessing.
3. **"What Should I Worry About?" Radar:** An automated risk engine that continuously scans cross-departmental records to identify organizational and technical vulnerabilities.
4. **14 Grounded Persona AI Agents:** Realistic, data-grounded simulations of 14 employees across Engineering, Finance, People & Ops, and Marketing.
5. **Strict Temporal Point-in-Time Gating:** Ensuring that queries evaluated as of a specific simulation date (e.g., Day 1: 16 Nov 2026) cannot leak information from later dates.

---

## 2. High-Level System Architecture

The system is organized into four modular layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                            │
│  • CLI Executive Cockpit (`src/cockpit.py`)                             │
│  • Persona Agent Interview Interface (`src/agents.py`)                  │
│  • "What Should I Worry About?" Radar View                              │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                             REASONING LAYER                             │
│  • Query Dispatcher & Intent Classifier                                 │
│  • Citation & Evidence Formatter (Doc, Sheet/Line, Date)                │
│  • Conflict & Uncertainty Detector (Refusal Gate)                       │
│  • Temporal Filter (Point-in-Time Isolation)                            │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                        GROUNDED PERSONA ENGINE                          │
│  • 14 Employee Personas (Eng: 5, Fin: 3, HR: 3, Mktg: 3)                │
│  • Profile Store: Facts (Keka/Zoho/Jira) + Inferred Context             │
│  • Interview & Query Dispatcher                                         │
└────────────────────────────────────▲────────────────────────────────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                    DATA INGESTION & RECONCILIATION                      │
│  • Data Loaders (Excel, PDF, EML, DOCX transcripts)                     │
│  • ASR Phonetic & Entity Normalization Engine                           │
│  • Cross-Source Reconciliation & Discrepancy Log                        │
│  • Storage: SQLite Database (`veloxa.db`) + JSON Evidence Catalog       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Breakdown

### 3.1 Data Ingestion & Storage Architecture
* **Storage Engine:** Local SQLite database (`veloxa.db`) paired with structured JSON index files.
  * **Why SQLite?** Provides zero-configuration setup, fully relational joins across HR, payroll, and GL data, instant startup from a fresh clone, and 100% reproducibility across environments without external services.
* **Ingestion Pipelines:**
  * **HRMS Parser:** Ingests `Employee_Master.xlsx` (19 employees) into normalized `employees` table.
  * **Finance Parsers:**
    * `Payroll_Register_Jan-Mar_2026.xlsx` into `payroll_records` table.
    * `GL_Export_Apr-Sep_2026.xlsx` into `general_ledger` table.
  * **Document & Email Parsers:**
    * `pypdf` parser for `Board_Update_*.pdf`.
    * Standard library `email` parser for `.eml` thread logs.
  * **Transcript Parser:**
    * DOCX XML parser for `T1` (CEO Kickoff) and `T2` (CFO Call).

### 3.2 Entity Resolution & ASR Normalization
Machine-generated transcripts introduce phonetic spelling errors and informal colloquialisms. The resolution engine maintains a canonical entity mapping:
* Spoken names: `"Pria"` -> `Priya Nair (VX007)`, `"Vicky"` -> `Vikram Menon (VX004)`, `"Fatima Shaikh"` -> `Fatima Sheikh (VX014)`.
* Tool names: `"Jeera"` -> `Jira`, `"Joho"` -> `Zoho Books`, `"Kayka"` -> `Keka HRMS`, `"Cult Amp"` -> `Culture Amp`, `"slag"` -> `Slack`, `"hub sport"` -> `HubSpot`.
* Vendor names: `"Sapphire Events Pvt Ltd"` and `"Saphire Event Mgmt"` are resolved to the same vendor entity (`Sapphire Events`).

### 3.3 Reconciliation & Discrepancy Engine
Before answering questions, the system compares spoken claims against primary ledger exports:
1. **Headcount Conflict:** T1 mentions "eighteen... one-eighty give or take", while Keka HRMS and Board updates confirm active team size is **19**.
2. **Burn Rate Conflict:** CFO Meera claims burn is "two point two lakhs a month", while Zoho GL records show monthly payroll alone is **Rs. 31.75 Lakhs**, WeWork rent is **Rs. 2.36 Lakhs**, and Board Updates state monthly burn is **Rs. 44L - 46L**.
3. **Payroll Discrepancy:** Rahul Verma (VX018) joined 3 Feb 2026, but Feb payroll shows 28 payable days (full month) processed by Karthik while Fatima was away, triggering an employee query email.

### 3.4 14 Grounded Persona Agents
The company has 19 total employees. Excluding CEO Ananya Rao (VX001), 2 Sales personnel (VX002 Manoj Kumar, VX008 Divya Reddy), and 2 Support personnel (VX016 Imran Siddiqui, VX019 Kavya Narayan), exactly **14 employees** span the core functional departments:
* **Engineering (5):** Vikram Menon (VP Eng, VX004), Priya Nair (Staff Eng, VX007), Arjun Das (Sr Frontend, VX009), Sneha Kulkarni (SRE, VX012), Rahul Verma (Backend Eng, VX018).
* **Finance (3):** Meera Iyer (CFO, VX003), Karthik Subramanian (FP&A Manager, VX010), Fatima Sheikh (Accounts & Payroll, VX014).
* **People & Operations (3):** Deepa Joshi (Head of People, VX005), Rohan Banerjee (Talent Partner, VX015), Lakshmi Pillai (HR & Office Exec, VX017).
* **Marketing (3):** Nikhil Bose (Head of Marketing, VX006), Aisha Khan (Performance Mktg, VX011), Siddharth Mehta (Product Mktg, VX013).

Each agent exposes an `ask(question)` interface that accesses their role data, managerial hierarchy, salary/payroll data, communications, and declared assumptions.

### 3.5 CXO Cockpit Query Engine & "What Should I Worry About?" Radar
* **Direct Q&A:** Accepts executive queries and generates answers structured with:
  * **Answer Text:** Concise executive summary.
  * **Citations:** Primary record pointers (`[GL_Export_Apr-Sep_2026.xlsx: Row 5]`).
  * **Confidence Level:** `HIGH`, `MEDIUM`, or `LOW`.
  * **Uncertainty / Refusal Notice:** Triggered when records conflict or data is unavailable.
* **Risk Radar ("What should I worry about?"):**
  Aggregates risk signals across four categories:
  1. *Financial Risk:* Burn rate mismatch between CFO verbal reporting (2.2L) and actual ledger (44L-46L).
  2. *Product/Delivery Risk:* Atlas (Routing v3) schedule slippage (delayed from September to post-August hardening).
  3. *Operational/Payroll Risk:* Unadjusted payroll overpayment for new backend engineer Rahul Verma.
  4. *People/Attrition Risk:* Notice period departure in Product Marketing (Siddharth Mehta exiting 31 Oct 2026).

### 3.6 Temporal Point-in-Time Gating
To prevent future leakage, every ingested artifact is tagged with its release pack day (`Day1_Mon_16Nov`, `Day2_Tue_17Nov`, etc.) and real-world date. Queries configured with a temporal boundary will strictly filter out any evidence released after that date.

---

## 4. Technology Stack

* **Language:** Python 3.10+
* **Database:** SQLite3 (standard library)
* **File Parsers:** `openpyxl` (Excel), `pypdf` (PDF), `email` (EML), XML parser (DOCX)
* **Testing:** `pytest` / `unittest`
* **Architecture Style:** Clean, modular, junior-friendly procedural & object-oriented code without unnecessary external dependencies.

---

## 5. One-Command Setup & Verification

```bash
# Setup and run from fresh clone
python -m src.ingest_day1
python -m src.cockpit --worry
pytest tests/
```
