# Veloxa CXO Cockpit - Transcript Notes & Source Contradictions (`TRANSCRIPT_NOTES.md`)

This document records all suspected Automated Speech Recognition (ASR) phonetic transcription errors, misheard names, incorrect numbers, and direct contradictions between spoken statements in transcripts and primary records in the data room.

---

## 1. Phonetic & Transcription Mishearings (ASR Artifacts)

| Ref ID | Transcript & Line | As Transcribed | Likely Intended Term | Primary Evidence & Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **TN-001** | T1 line 7 | "eighteen people ('one-eighty, give or take')" | 18 or 19 people | `Employee_Master.xlsx` lists exactly 19 employees. `Board_Update_Apr-Jun_2026.pdf` and `Board_Update_Jul-Sep_2026.pdf` both report "Team: 19". The ASR software misheard the speaker saying "around eighteen or nineteen" as "one-eighty". |
| **TN-002** | T1 line 13 | "Jeera board" | Jira (Atlassian) | Phonetic spelling of Jira. Later files confirm Jira ATLAS export. |
| **TN-003** | T1 line 15 | "Pria" | Priya Nair (VX007) | `Employee_Master.xlsx` lists Priya Nair as Staff Engineer in Engineering. |
| **TN-004** | T1 line 17 | "Cult Amp" | Culture Amp | Well-known employee pulse survey platform mentioned in HR exports. |
| **TN-005** | T1 line 24 | "slag channel" | Slack channel | Standard phonetic mishearing of Slack. |
| **TN-006** | T1 line 23 | "hub sport export" | HubSpot export | Standard phonetic mishearing of HubSpot CRM. |
| **TN-007** | T2 line 13 | "Joho books" | Zoho Books | Primary financial ledger export is named `GL_Export_Apr-Sep_2026.xlsx` from Zoho Books. |
| **TN-008** | T2 line 16 | "Kayka" | Keka HRMS | HRMS export is explicitly titled `Keka HRMS export` (`Employee_Master.xlsx`). |
| **TN-009** | T2 line 20 | "Fatima Shaikh" | Fatima Sheikh (VX014) | Listed as Fatima Sheikh, Accounts & Payroll Executive, in `Employee_Master.xlsx`. |
| **TN-010** | T2 line 28 | "Vicky" | Vikram Menon (VX004) | Nickname for Vikram Menon, VP Engineering. |
| **TN-011** | GL Voucher JV-0904 | "Saphire Event Mgmt" | Sapphire Events Pvt Ltd | In voucher JV-0846, vendor is entered as "Sapphire Events Pvt Ltd". In JV-0904, it is entered as "Saphire Event Mgmt". Both represent the logistics summit event vendor. |

---

## 2. Cross-Source Contradictions & Reconciliations

### Conflict 1: Headcount (180 vs 19)
* **Spoken Claim:** In T1, Ananya remarks the company is roughly "one-eighty, give or take" (and candidate brief says 180-person company).
* **Hard Data:** `Employee_Master.xlsx` has exactly 19 active employees. Board updates for Q1 and Q2 2026 both explicitly report "Team: 19".
* **Resolution & Defense:** We trust the primary HRMS export and quarterly Board reports over the conversational remark. Veloxa is a tight-knit 19-person startup. Ananya either made a joking exaggeration or the speech recognizer confused "eighteen" with "one-eighty".

### Conflict 2: Monthly Burn Rate (Rs. 2.2 Lakhs vs Rs. 44–46 Lakhs)
* **Spoken Claim:** In T2, CFO Meera states: *"Burn has been two point two lakhs a month, sometimes two point five."* In T1, Ananya also mentions *"burn is around two point two (unit not stated)"*.
* **Hard Data:**
  * `GL_Export_Apr-Sep_2026.xlsx` reveals monthly payroll alone is **Rs. 31,75,000** (`PAY-APR` through `PAY-SEP`).
  * Monthly WeWork office rent is **Rs. 2,36,000** (`RENT-APR` through `RENT-SEP`).
  * AWS cloud infrastructure costs **Rs. 1.81L to Rs. 2.48L** monthly.
  * Google Ads cost **Rs. 76k to Rs. 94k** monthly.
  * `Board_Update_Apr-Jun_2026.pdf` reports "Monthly burn: Rs. 46 L".
  * `Board_Update_Jul-Sep_2026.pdf` reports "Monthly burn: Rs. 44 L".
* **Resolution & Defense:** Meera's statement of "2.2 lakhs" cannot be the total net burn of the company because payroll alone is 31.75 Lakhs. Either:
  1. Meera was referring to non-payroll discretionary opex (or cloud spend ~Rs. 2.2L).
  2. The speech engine misheard "forty-two lakhs" as "two point two lakhs".
  3. Meera deliberately obscured the real burn from the CEO (supported by her remark: *"Individual salaries must never show up in anything Ananya sees, only totals"*).
  * **Cockpit Action:** The Cockpit refuses to validate "2.2 lakhs" as true company burn and will present the primary ledger figures (Rs. 44L–46L) while flagging Meera's spoken discrepancy.

### Conflict 3: Annual Recurring Revenue (ARR) (Rs. 42-45 Cr vs Rs. 5.8-6.1 Cr)
* **Spoken Claim:** In T1, Ananya estimates ARR is *"around forty-two crore, maybe forty-five now"*. In T2, Meera states ARR at the start of the year was *"forty-eight"*.
* **Hard Data:**
  * `Board_Update_Apr-Jun_2026.pdf` reports ARR as **Rs. 5.8 Cr** (61 customers).
  * `Board_Update_Jul-Sep_2026.pdf` reports ARR as **Rs. 6.1 Cr** (66 customers).
* **Resolution & Defense:** An ARR of 42–45 Crore across 61–66 customers would imply an average ACV of ~Rs. 70 Lakhs/customer, which is inconsistent with Veloxa's team size (19 people) and burn rate. If ARR is Rs. 5.8 Cr annually, that equals ~Rs. 48.3 Lakhs Monthly Recurring Revenue (MRR). Meera saying "forty-eight" in T2 refers to **48 Lakhs MRR**, and Ananya confused 42–45 Lakhs MRR with Crores.
  * **Cockpit Action:** Cite Board updates (Rs. 6.1 Cr ARR) and flag Ananya's verbal statement as an unverified unit misstatement.

### Conflict 4: Routing Engine Atlas GA Target (September 15 vs Delayed Post-August)
* **Spoken Claim:** In T1, Ananya expresses urgency: *"routing engine version three was promised to some customers by the festive season and she is not sure it will make it."*
* **Hard Data:**
  * `Board_Update_Apr-Jun_2026.pdf` listed GA for 15 September.
  * `Board_Update_Jul-Sep_2026.pdf` explicitly announces: *"We moved GA to absorb unplanned reliability work after a difficult August; the engine itself is feature-complete."*
  * GL record `JV-0902` confirms emergency external contractor *Patil Infra Services* was hired for on-call support from 18–31 August (Rs. 70,800).
* **Resolution & Defense:** Ananya's suspicion that Atlas would miss the festive season target was correct. The board update and GL prove an outage/reliability crisis occurred in late August, delaying release.

### Conflict 5: Rahul Verma February Payroll Overpayment
* **Spoken Claim:** Call T2 notes Fatima was out for her wedding and Kartik handled payroll ("that month was messy").
* **Hard Data:**
  * Rahul joined on 2026-02-03 (`Employee_Master.xlsx`).
  * Feb payroll was processed by 'KS' (Karthik Subramanian) for full 28 days (Rs. 1,10,000 gross).
  * Email `02.eml` shows Rahul queried the excess amount.
  * Email `03.eml` shows Fatima promised to check, but March payroll (`Payroll_Register_Jan-Mar_2026.xlsx`) shows no recovery adjustment.
* **Resolution & Defense:** Validated payroll calculation error caused by temporary handover to an unqualified person (Karthik) during wedding leave.
