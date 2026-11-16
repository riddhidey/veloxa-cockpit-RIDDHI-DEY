# Veloxa CXO Cockpit - AI Usage & Audit Log (`AI_LOG.md`)

This log honestly records all tasks delegated to AI assistants, instances where the AI generated incorrect statements, hallucinations, or ungrounded assumptions, and how human review identified and corrected them.

---

### Entry 1: 2026-11-16 — Headcount Hallucination Check
* **Task Delegated to AI:** Parse `Candidate_Brief.docx` and summarize the company profile.
* **AI Output/Suggestion:** The AI summarized: *"Veloxa Technologies is a 180-person B2B SaaS startup founded in Bengaluru..."*
* **Where AI Was Wrong:** The AI accepted the opening brief sentence literally without cross-referencing the primary data room files.
* **Human Discovery & Correction:** When we inspected `Employee_Master.xlsx`, there were only 19 employees listed. Furthermore, `Board_Update_Apr-Jun_2026.pdf` and `Board_Update_Jul-Sep_2026.pdf` explicitly state: *"Team: 19"*. The AI failed to notice that in transcript T1, the ASR transcript read: *"Company is roughly eighteen people ('one-eighty, give or take')"*. The prompt author intentionally placed this discrepancy in the brief to test whether the candidate verifies the data room.
* **Correction Made:** Corrected the company profile in all architecture and assumption files to 19 employees, logging the ASR mishearing in `TRANSCRIPT_NOTES.md`.

---

### Entry 2: 2026-11-16 — Burn Rate Verification
* **Task Delegated to AI:** Check the monthly burn rate from the CFO interview (T2).
* **AI Output/Suggestion:** The AI reported: *"The monthly burn rate is Rs. 2.2 Lakhs as stated by CFO Meera Iyer."*
* **Where AI Was Wrong:** The AI treated the CFO's spoken statement as ground truth without validating it against the financial ledger.
* **Human Discovery & Correction:** We wrote a script to inspect `GL_Export_Apr-Sep_2026.xlsx`. The general ledger proved that salaries alone (`PAY-APR` to `PAY-SEP`) were Rs. 31,75,000 every single month, office rent was Rs. 2,36,000, and AWS cloud spend was over Rs. 2,00,000. True monthly burn was Rs. 44L to 46L (as confirmed in Board updates). The AI's answer was wildly inaccurate and would have misled the CEO.
* **Correction Made:** Established the principle of dual reporting in `DECISIONS.md`. When asked about burn, the cockpit will report the ledger figures and explicitly flag the CFO's spoken claim as a conflict.

---

### Entry 3: 2026-11-16 — Rahul Verma Payroll Investigation
* **Task Delegated to AI:** Review email threads `01.eml`, `02.eml`, and `03.eml` and connect them to payroll records.
* **AI Output/Suggestion:** The AI claimed that Rahul Verma's payslip was disputed because of tax deduction miscalculations.
* **Where AI Was Wrong:** The AI hallucinated a standard tax issue rather than checking the calendar dates and join dates.
* **Human Discovery & Correction:** In `Employee_Master.xlsx`, Rahul Verma's join date was `2026-02-03` (joined 3 days into February). In `Payroll_Register_Jan-Mar_2026.xlsx`, February had 28 days, and Rahul was paid for a full 28 days (`Days Payable: 28`, Gross: Rs. 1,10,000) by Karthik Subramanian (`KS`), who ran payroll without prorating. Rahul noticed his pay was unexpectedly high for a partial month (Email 02).
* **Correction Made:** Logged the exact overpayment and root cause in `TRANSCRIPT_NOTES.md` (TN-012) and `ASSUMPTIONS.md` (A-003).

---

### Entry 4: 2026-11-16 — 14 Persona Roster Identification
* **Task Delegated to AI:** Identify the 14 employees to be modeled as persona agents.
* **AI Output/Suggestion:** The AI initially picked 14 random employees, including Sales and Customer Support, leaving out some engineers.
* **Where AI Was Wrong:** The AI ignored the prompt's instruction: *"start with 14 people across engineering, finance, HR and marketing"*.
* **Human Discovery & Correction:** The full company has 19 employees. Excluding the CEO (1), Sales (2), and Support (2) yields exactly 14 employees across Engineering (5), Finance (3), People & Ops (3), and Marketing (3).
* **Correction Made:** Explicitly mapped the exact 14 employee IDs in `ARCHITECTURE.md` and `DECISIONS.md`.
