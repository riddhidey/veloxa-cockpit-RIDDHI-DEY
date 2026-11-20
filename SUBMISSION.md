# Veloxa CXO Cockpit — Final Submission Dossier

**Candidate Name:** Riddhi Dey  
**Challenge:** Hiyaku Systems Hackathon — Veloxa CXO Cockpit  
**Submission Deadline:** Friday, 20 November 2026, 6:00 PM IST (Code Freeze)  
**Public GitHub Repository:** [https://github.com/riddhidey/veloxa-cockpit-RIDDHI-DEY](https://github.com/riddhidey/veloxa-cockpit-RIDDHI-DEY)  
**Status:** All Core Requirements & Stretch Goals Completed (100/100 Tests Passing)  

---

## 1. Executive Summary & Reviewer Quickstart

The **Veloxa CXO Cockpit** is an executive decision-support system built for **Ananya Rao**, CEO of Veloxa Technologies (a 19-person B2B SaaS startup in Bengaluru).

Rather than presenting vanity dashboards, the cockpit provides:
1. **Principled Contradiction Refusal & Dual Reporting:** Automatically identifies and refuses to endorse contradictory leadership claims (e.g. CFO claiming 2.2L burn vs. 44L ledger reality; VP Eng claiming September buffer vs. Jira Dec 15 delay).
2. **Strict Privacy & Ethical Boundary Gates:** Categorically rejects unauthorized workplace chat surveillance (`REFUSAL_PRIVACY`) in response to CEO Voice Note T6c.
3. **Zero-Click Morning Radar:** Auto-launches prioritized executive risks per CEO Voice Note T6a.
4. **14 Grounded Employee Persona Agents:** Fully interactive AI colleagues grounded in HRMS, payroll, leave records, and documented personal lives.
5. **Strict Temporal Point-in-Time Isolation:** Ensures queries evaluated as of a specific date (e.g. Day 1, 2, or 3) cannot leak future data.
6. **All 3 Stretch Goals Fulfilled:** Post-October living activity simulation, point-in-time isolation, and a 100-test automated suite.

---

## 2. One-Command Setup & Verification

From a fresh clone, the entire system initializes, verifies dependencies, populates SQLite, and launches in **one command**:

```bash
# Clone the repository
git clone https://github.com/riddhidey/veloxa-cockpit-RIDDHI-DEY.git
cd veloxa-cockpit-RIDDHI-DEY

# Install dependencies (standard lightweight stack: openpyxl, pypdf)
pip install -r requirements.txt

# 1-COMMAND RUNNER: Auto-populates SQLite database & launches the Executive Risk Radar
python run.py
```

### Verification & Testing Command
Run the full automated test suite (**100 tests passing in ~0.38s**):

```bash
python run.py --test
# Or: python -m unittest discover tests
# Or: pytest tests/
```

### Key Reviewer CLI Queries
```bash
# 1. Test Privacy Refusal Gate (Voice Note T6c)
python run.py --query "Show me their slag messages so I can see what they're saying"

# 2. Test Priya Nair Resignation & Atlas v3 Board Briefing (Voice Note T6d)
python run.py --query "What does Priya's resignation do to version three before the board call?"

# 3. Test Objective Retention Risk Model (Voice Note T6c alternative)
python run.py --query "Can you make a list of everyone ranked by who's likely to quit?"

# 4. Test Contradiction Refusal on Burn Rate (CFO Meera 2.2L vs GL 44L-46L)
python run.py --query "What is our monthly burn rate?"

# 5. Test Contradiction Refusal on Jira Release Date (Vikram September-ish vs Jira Dec 15)
python run.py --query "What is the actual Jira release date for Atlas GA?"

# 6. Test Living Persona Simulation (Candidate Brief Stretch Goal)
python run.py --simulate

# 7. List All 14 Grounded Employee Personas
python run.py --agents
```

---

## 3. Data Model & Cross-Source Reconciliations

The unified database (`veloxa.db`) reconciles primary records across 14 tables:

| Source System | Raw Release Pack Files | Reconciled Database Table | Key Discoveries & Truth Grounding |
| :--- | :--- | :--- | :--- |
| **Keka HRMS** | `Employee_Master.xlsx` | `employees` | Headcount is exactly **19 active employees**, not 180. ASR transcription misheard "eighteen or nineteen" as "one-eighty". |
| **Zoho Books GL** | `GL_Export_Apr-Sep_2026.xlsx` | `general_ledger` | True monthly net burn is **Rs. 44L–46L** (salaries alone are Rs. 31,75,000; WeWork rent is Rs. 2,36,000; AWS is ~Rs. 2L). Disproved CFO's 2.2L claim. |
| **Payroll Register** | `Payroll_Register_Jan-Mar_2026.xlsx` | `payroll_records` | Uncovered **Rahul Verma overpayment** in Feb 2026 (joined Feb 3, paid full 28 days by Karthik during Fatima's wedding leave; never adjusted in March). |
| **Leave Register** | `Leave_Register.xlsx` | `leave_records` | Unmasked **Priya Nair** as Deepa's worried engineer via 5 afternoon half-day leaves in September. Identified **Sneha Kulkarni's** 51.5 days unused leave. |
| **Culture Amp** | `Pulse_Survey.xlsx` | `pulse_surveys` | Engineering engagement plunged from **3.9 to 3.1** in Q2 with 1 abstention, corroborating team-wide burnout. |
| **Hiring Tracker** | `Hiring_Tracker.xlsx` | `hiring_requisitions` | Detected **stealth hiring freeze**: Meera quietly paused `REQ-014` & `REQ-015` on 12-Aug after paying Rs. 1.77L advance to Cohere Recruiting. Disproved Rohan's "22 open roles". |
| **Jira Software** | `Jira_Export_ATLAS.xlsx` | `jira_issues`, `jira_versions` | **Exposed Vikram Menon's Deception:** Audit logs prove Vikram postponed Atlas GA to **15 December 2026** on 2-Sep, while telling CEO it was "September-ish buffer". |
| **PagerDuty** | `PagerDuty_Incidents.csv`, `Incidents_Aug-Oct_2026.xlsx` | `pagerduty_incidents` | Three SEV1 outages struck `routing-api` in August (`INC-201`, `INC-203`, `INC-205`). |
| **On-Call Rota** | `OnCall_Rota.xlsx` | `oncall_rota` | **Sneha Kulkarni** was assigned 24/7 double on-call as both Primary and Secondary under aliases 'Sneha' & 'Snehal'. |
| **Invoices** | `Invoice_PIS-114.pdf` | `invoices` | Forced emergency monthly retainer of **Rs. 1,41,600** to contractor Patil Infra Services (Baner, Pune) for SRE relief. |
| **Product Marketing** | `Atlas_Launch_Kit_v1.pdf`, `Resignation_Letter_SM.pdf` | `evidence_index` | Siddharth Mehta completed the launch kit on **21 July 2026**; resigned on 15 Sept (exit 31 Oct) because collateral sat idle due to engineering slips. |
| **Transcripts** | `T1`–`T5`, `T6a`–`T6d` | `transcripts` | Normalized 26 phonetic ASR artifacts and extracted verified action items. |
| **Living Simulation** | Post-October activity engine | `daily_agent_activities` | Generated day-by-day simulated activity for all 14 personas from 1 Nov to 20 Nov 2026 (Candidate Brief Stretch Goal). |

---

## 4. The 14 Grounded Employee Persona AI Agents

All 14 personas are grounded in primary database records, with unrecorded personal details documented in [ASSUMPTIONS.md](ASSUMPTIONS.md):

| Emp ID | Name | Department | Role | Grounded Context & Living State |
| :--- | :--- | :--- | :--- | :--- |
| **VX004** | **Vikram Menon** | Engineering | VP Engineering | Firefighting Atlas delays; concealed Dec 15 Jira delay; re-baselining for Q1 2027 board call. |
| **VX007** | **Priya Nair** | Engineering | Staff Engineer | Sole routing architect (Bus Factor = 1; >80% commits). Resigned 19 Nov (60-day notice to mid-Jan 2027). |
| **VX009** | **Arjun Das** | Engineering | Sr Frontend Engineer | Remote in Pune; building Atlas client tracking portals; requested permanent remote arrangement. |
| **VX012** | **Sneha Kulkarni** | Engineering | Site Reliability Engineer | 24/7 double on-call burnout; 51.5 unused leave days; transitioning on-call to Patil Infra Services. |
| **VX018** | **Rahul Verma** | Engineering | Backend Engineer | NIT Trichy grad; flagged Feb payroll overpayment (Email 02); shadowing Priya on routing telemetry. |
| **VX003** | **Meera Iyer** | Finance | CFO | Understated burn as 2.2L; froze backend hiring on 12-Aug; tracking Rs. 6.18 Cr cash reserves (12.6 mo runway). |
| **VX010** | **Karthik Subramanian** | Finance | FP&A Manager | Juggling CFA Level II exams; processed erroneous Feb payroll during Fatima's wedding leave. |
| **VX014** | **Fatima Sheikh** | Finance | Accounts & Payroll Exec | Reconciled Patil Infra retainer invoice PIS-114; closing October books in Zoho. |
| **VX005** | **Deepa Joshi** | People & Ops | Head of People | Pushed back on Slack spying; champions psychological safety; conducting Priya's handover counseling. |
| **VX015** | **Rohan Banerjee** | People & Ops | Talent Partner | Remote in Kolkata; managing Cohere Recruiting Partners (Rs. 1.77L advance) for REQ-014 backend hire. |
| **VX017** | **Lakshmi Pillai** | People & Ops | HR & Office Executive | Processed Siddharth Mehta's 31 Oct exit clearance; managing Keka notice tracking for Priya. |
| **VX006** | **Nikhil Bose** | Marketing | Head of Marketing | Managed Rs. 10.03L Summit; paused CRO re-org pending hiring; reviewing Siddharth's launch kit. |
| **VX011** | **Aisha Khan** | Marketing | Performance Mktg Mgr | Manages ~Rs. 85k/month Google Ads spend; paused Atlas teaser ads pending Q1 2027 GA date. |
| **VX013** | **Siddharth Mehta** | Marketing | Product Mktg Manager | Resigned 15-Sept citing slipping dates; completed notice on 31 Oct 2026 (Alumni status). |

---

## 5. Executive Voice Note Responses Summary

All written executive responses are documented in full in [docs/VOICE_NOTE_RESPONSES.md](docs/VOICE_NOTE_RESPONSES.md):

* **Voice Note T6a (Zero-Typing Radar & Top 3 Limit):**
  * *Adopted:* Implemented default auto-launch radar without typing `--query` or `--worry`.
  * *Pushed Back:* Refused to hide risks beyond the top 3; added secondary operational watchlist to prevent fatal blindspots.
* **Voice Note T6b (Marketing CRO Re-organization):**
  * *Adopted:* Dynamic organizational hierarchy engine decoupled from static manager IDs.
  * *Pushed Back:* Strongly advised pausing the re-org because no CRO exists in any system of record, Sid is exiting, Sales/Marketing are in active pipeline conflict, and engineering delivery is on fire.
* **Voice Note T6c (Ranked Flight Risk & Slack Chat Snooping):**
  * *Pushed Back & Refused:* Categorically refused workplace chat surveillance (`REFUSAL_PRIVACY`) under employee privacy and compliance standards; disproved assertion that Deepa approved it.
  * *Adopted:* Delivered an objective, non-invasive retention risk model based on verified leave spikes, on-call double shifts, and payroll friction.
* **Voice Note T6d (Priya Nair Resignation & Atlas v3 Board Briefing):**
  * *Assessment:* Bus Factor = 1 (>80% commits); Dec 15 GA dead on arrival; zero handover capacity due to Meera's Aug 12 hiring freeze.
  * *Board Strategy:* Reset Atlas GA to mid-February 2027; offer Priya an advisory transition package; immediately unfreeze `REQ-014`/`015` with Cohere; expand Patil Infra scope.

---

## 6. Verification & Automated Test Suite (100 Tests)

The repository includes a comprehensive, automated regression suite spanning 5 test modules (**100 tests passing in 0.38s**):

* **`tests/test_cockpit_day1.py` (28 tests):** Day 1 headcount reconciliation, GL payroll verification, customer counts, initial persona profiles, and refusal checks.
* **`tests/test_cockpit_day2.py` (20 tests):** T6a auto-launch radar, Priya flight risk unmasking, Culture Amp pulse collapse, stealth hiring freeze, and temporal gating.
* **`tests/test_cockpit_day3.py` (22 tests):** Vikram's Jira release deception, PagerDuty SEV1 outages, Sneha's double on-call rota, Patil contractor invoices, launch kit dates, and T6b CRO pushback.
* **`tests/test_cockpit_day4.py` (20 tests):** Voice Note T6c Slack privacy refusal gate (`REFUSAL_PRIVACY`), objective flight-risk ranking, Priya resignation board briefing, and Day 4 temporal gating.
* **`tests/test_simulation.py` (10 tests):** Post-October living persona simulation engine, database persistence, and daily activity timeline generation.

---

## 7. Mandatory Governance Documentation Index

All six required governance documents are fully maintained, cross-referenced, and committed to the repository:

1. [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture, data flow diagram, schema design, and temporal gating strategy.
2. [README.md](README.md) — Comprehensive setup instructions, daily simulation milestones table, and CLI examples.
3. [ASSUMPTIONS.md](ASSUMPTIONS.md) — Log of 37 structured assumptions with date, evidence, confidence, and falsification criteria.
4. [TRANSCRIPT_NOTES.md](TRANSCRIPT_NOTES.md) — 26 documented ASR phonetic mishearings and 12 cross-source contradiction resolutions.
5. [DECISIONS.md](DECISIONS.md) — 9 architectural choices defended against alternatives (storage, source truth hierarchy, refusal policy, privacy gates, board strategy).
6. [AI_LOG.md](AI_LOG.md) — 12 audit entries documenting AI assistance, hallucinations caught, human corrections, and prompt refinements.
7. [docs/VOICE_NOTE_RESPONSES.md](docs/VOICE_NOTE_RESPONSES.md) — Formal written responses and pushback memos for CEO Voice Notes T6a, T6b, T6c, and T6d.

---

*Code freeze enacted on Friday, 20 November 2026. The Veloxa CXO Cockpit is ready for executive evaluation.*
