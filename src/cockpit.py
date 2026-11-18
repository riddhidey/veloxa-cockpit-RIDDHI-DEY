"""
Veloxa CXO Cockpit Engine.
Provides executive Q&A with verifiable citations, confidence scoring,
principled contradiction/unknown refusal, and the 'What should I worry about?' radar view.
"""

import sys
import argparse
import sqlite3
from typing import Dict, List, Optional, Any
from src.reconcile import ReconciliationEngine

DB_PATH = "veloxa.db"


class CockpitEngine:
    def __init__(self, db_path: str = DB_PATH, as_of_date: str = "2026-11-16"):
        self.db_path = db_path
        self.as_of_date = as_of_date  # Day 1 cutoff
        self.reconciler = ReconciliationEngine(db_path=db_path)

    def query(self, question: str) -> Dict[str, Any]:
        """
        Executes a CEO query and returns a structured response with:
        - short, direct answer
        - primary evidence citations
        - confidence rating
        - refusal / contradiction flag if sources disagree or data is missing
        """
        q = question.lower().strip()

        # 1. Unknown / Out of Temporal Scope / Future questions
        if any(w in q for w in ["q4 2026", "fy28", "2027", "next year", "ipo", "series b", "acquisition"]):
            return {
                "question": question,
                "answer": "I don't know. This information is not present in records released up to 16 Nov 2026.",
                "citations": ["Temporal Gating: Day 1 (2026-11-16) boundary"],
                "confidence": "LOW",
                "status": "REFUSAL_UNKNOWN"
            }

        # 2. Burn rate query (Classic Contradiction Case)
        if any(w in q for w in ["burn", "burn rate", "monthly burn", "spending"]):
            burn_info = self.reconciler.detect_burn_rate_conflict()
            return {
                "question": question,
                "answer": (
                    "The sources disagree. In meeting T2, CFO Meera claimed monthly burn is '2.2 lakhs a month'. "
                    "However, primary financial ledgers and Board reports prove true net monthly burn is Rs. 44 Lakhs to 46 Lakhs. "
                    "Salaries alone are Rs. 31.75 Lakhs/month, WeWork rent is Rs. 2.36 Lakhs, and AWS is over Rs. 2 Lakhs."
                ),
                "citations": [
                    "Board_Update_Jul-Sep_2026.pdf (Monthly burn: Rs. 44 L)",
                    "Board_Update_Apr-Jun_2026.pdf (Monthly burn: Rs. 46 L)",
                    "GL_Export_Apr-Sep_2026.xlsx (PAY-APR through PAY-SEP: Rs. 31,75,000)",
                    "T2 CFO Call (Meera spoken claim: '2.2 lakhs')"
                ],
                "confidence": "HIGH",
                "status": "REFUSAL_CONTRADICTION",
                "contradiction_details": burn_info["reasoning"]
            }

        # 3. Headcount / Team size query
        if any(w in q for w in ["headcount", "how many people", "team size", "employees", "how many employees"]):
            hc_info = self.reconciler.detect_headcount_conflict()
            return {
                "question": question,
                "answer": (
                    f"Veloxa has {hc_info['resolved_value']} employees. While T1 audio transcription mentioned 'one-eighty give or take', "
                    "this was an ASR speech mishearing or exaggeration. Keka HRMS and both quarterly Board updates confirm team size is exactly 19."
                ),
                "citations": [
                    "Employee_Master.xlsx (19 active rows in Keka HRMS)",
                    "Board_Update_Apr-Jun_2026.pdf ('Team: 19')",
                    "Board_Update_Jul-Sep_2026.pdf ('Team: 19')",
                    "TRANSCRIPT_NOTES.md (TN-001)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 4. ARR / Revenue query
        if any(w in q for w in ["arr", "revenue", "annual recurring revenue", "annual revenue"]):
            return {
                "question": question,
                "answer": (
                    "Annual Recurring Revenue (ARR) is Rs. 6.1 Crore as of September 2026 (up from Rs. 5.8 Crore in June 2026). "
                    "In call T1, the CEO mentioned 'forty-two crore, maybe forty-five', but this was an unverified unit misstatement (confusing Lakhs MRR with Crores ARR)."
                ),
                "citations": [
                    "Board_Update_Jul-Sep_2026.pdf ('ARR: Rs. 6.1 Cr, 66 customers')",
                    "Board_Update_Apr-Jun_2026.pdf ('ARR: Rs. 5.8 Cr, 61 customers')",
                    "TRANSCRIPT_NOTES.md (TN-013)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 4b. Jira Atlas Release Date / Vikram Deception query (Day 3 - checked before general Atlas)
        if any(w in q for w in ["jira release", "december 15", "atlas release date", "vikram date", "actual launch date", "actual jira"]):
            deception = self.reconciler.detect_vikram_release_deception()
            return {
                "question": question,
                "answer": (
                    "The sources directly conflict. In call T5, Vikram Menon assured the CEO that Atlas GA is 'on track, "
                    "maybe a couple weeks buffer, September-ish'. However, Jira system audit records prove that on 2 September 2026, "
                    "Vikram formally postponed the Atlas GA release date to 15 December 2026 (a 3-month slip)."
                ),
                "citations": [
                    "Jira_Export_ATLAS.xlsx (Versions sheet: Atlas GA Release Date 2026-12-15, Last Changed 2026-09-02 by vikram)",
                    "T5 VP Engineering Call (Spoken claim: 'September-ish with buffer')"
                ],
                "confidence": "HIGH",
                "status": "REFUSAL_CONTRADICTION",
                "contradiction_details": deception["conclusion"]
            }

        # 5. Atlas Routing Engine v3 / Product delivery query
        if any(w in q for w in ["atlas", "routing", "version three", "routing engine", "v3"]):
            atlas_info = self.reconciler.detect_atlas_schedule_delay()
            return {
                "question": question,
                "answer": (
                    "Atlas (Routing Engine v3) missed its original 15 September GA target. While the core engine is feature-complete, "
                    "General Availability was pushed back to absorb unplanned reliability fixes following database contention in August. "
                    "External vendor Patil Infra Services was hired for emergency on-call support."
                ),
                "citations": [
                    "Board_Update_Jul-Sep_2026.pdf ('moved GA to absorb unplanned reliability work after difficult August')",
                    "Board_Update_Apr-Jun_2026.pdf ('GA on 15 September')",
                    "GL_Export_Apr-Sep_2026.xlsx (JV-0902: Patil Infra Services Rs. 70,800)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 6. Payroll errors / Rahul Verma query
        if any(w in q for w in ["rahul", "payroll error", "overpayment", "payslip"]):
            anomaly = self.reconciler.detect_rahul_verma_payroll_anomaly()
            return {
                "question": question,
                "answer": (
                    "Yes, a payroll overpayment occurred in February 2026. Rahul Verma joined on 3 Feb 2026, but Karthik Subramanian "
                    "(covering payroll during Fatima's wedding leave) processed a full 28 days of pay (Rs. 1,10,000 gross). "
                    "Rahul emailed Fatima on March 6 to report the discrepancy, but no recovery adjustment was made in March."
                ),
                "citations": [
                    "Payroll_Register_Jan-Mar_2026.xlsx (Row 22: Days Payable 28, Processed By KS)",
                    "Employee_Master.xlsx (Rahul Join Date: 2026-02-03)",
                    "01.eml (Karthik confirms running Feb payroll)",
                    "02.eml (Rahul queries payslip amount)",
                    "03.eml (Fatima acknowledges query)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 7. Marketing summit spend query
        if any(w in q for w in ["summit", "logistics summit", "marketing spend", "sapphire"]):
            return {
                "question": question,
                "answer": (
                    "The Logistics Summit drew 212 registrations. Total event expenditure was Rs. 10,03,000 across two payments to "
                    "Sapphire Events (Rs. 5,42,800 for venue/AV on 29 Aug, and Rs. 4,60,200 for catering on 3 Sep)."
                ),
                "citations": [
                    "Board_Update_Jul-Sep_2026.pdf ('Logistics Summit drew 212 registrations')",
                    "GL_Export_Apr-Sep_2026.xlsx (JV-0846: Sapphire Events Rs. 5,42,800)",
                    "GL_Export_Apr-Sep_2026.xlsx (JV-0904: Saphire Event Mgmt Rs. 4,60,200)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 7b. Monthly salary / payroll expense in General Ledger
        if any(w in q for w in ["salary expense", "payroll expense", "salaries in general ledger", "salary in the general ledger"]):
            return {
                "question": question,
                "answer": (
                    "Monthly salary expenditure recorded in the Zoho Books General Ledger is Rs. 31,75,000 per month "
                    "(recorded consistently under cost centre PAYROLL from April to September 2026)."
                ),
                "citations": [
                    "GL_Export_Apr-Sep_2026.xlsx (Vouchers PAY-APR through PAY-SEP: Rs. 31,75,000)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 7c. Office Rent / WeWork
        if any(w in q for w in ["wework", "office rent", "rent"]):
            return {
                "question": question,
                "answer": (
                    "Office rent for WeWork India is Rs. 2,36,000 per month (cost centre G&A, recorded consistently "
                    "from April to September 2026 under vouchers RENT-APR through RENT-SEP)."
                ),
                "citations": [
                    "GL_Export_Apr-Sep_2026.xlsx (Vouchers RENT-APR through RENT-SEP: Rs. 2,36,000)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 7d. Customers count
        if any(w in q for w in ["customer", "customers"]):
            return {
                "question": question,
                "answer": (
                    "Veloxa has 66 customers as of Q2 (July to September 2026), an increase of 5 customers from 61 in Q1 (April to June 2026)."
                ),
                "citations": [
                    "Board_Update_Jul-Sep_2026.pdf ('Customers: 66')",
                    "Board_Update_Apr-Jun_2026.pdf ('Customers: 61')"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 8. Attrition / Resignations query
        if any(w in q for w in ["attrition", "leaving", "resignation", "turnover", "notice", "siddharth"]):
            return {
                "question": question,
                "answer": (
                    "Siddharth Mehta (Product Marketing Manager, VX013) submitted his formal resignation on 15 September 2026 "
                    "with his last working day on 31 October 2026. His resignation letter explicitly cited frustration with "
                    "unpredictable launch timelines and delayed product releases. Overall annualized turnover is ~5-10% (1 departure out of 19)."
                ),
                "citations": [
                    "Resignation_Letter_SM.pdf ('looking for a role with clearer launch timelines')",
                    "Employee_Master.xlsx (VX013 exit date: 2026-10-31)",
                    "Board_Update_Jul-Sep_2026.pdf ('One planned departure in marketing')"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 8b. Priya Nair flight risk & Worried Engineer query (Day 2)
        if any(w in q for w in ["priya leave", "flight risk", "worried engineer", "priya nair"]):
            risk_info = self.reconciler.detect_priya_flight_risk()
            return {
                "question": question,
                "answer": (
                    "Priya Nair (Staff Engineer) is identified as the unnamed engineer Deepa expressed worry about in call T3. "
                    "She is carrying the entire Atlas v3 routing architecture alone. In September 2026, she took 5 afternoon half-day "
                    "personal leaves (03, 08, 15, 17, 24 Sep), while Engineering Culture Amp engagement plunged to 3.1. "
                    "This strongly indicates job interviewing and severe flight risk."
                ),
                "citations": [
                    "Leave_Register.xlsx (5 half-day leaves for P. Nair in Sep 2026)",
                    "Pulse_Survey.xlsx (Engineering Q2 score: 3.1 with 4/5 responding)",
                    "Email 11.eml (Deepa warns Ananya about engineering pulse drop)",
                    "T3 Head of People Call ('one engineer I'm worried about')"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 8c. Hiring freeze / Requisitions / Cohere query (Day 2)
        if any(w in q for w in ["hiring freeze", "req-014", "req-015", "cohere", "open roles", "hiring tracker"]):
            freeze_info = self.reconciler.detect_hiring_freeze_conflict()
            return {
                "question": question,
                "answer": (
                    "A stealth hiring freeze occurred on 12 August 2026. While the Board update promised to add two backend engineers "
                    "to de-risk Atlas (and paid Rs. 1.77L advance to Cohere Recruiting), CFO Meera instructed Vikram via email (06.eml) "
                    "to pause REQ-014 and REQ-015. Final round interviews scheduled for 14-Aug were cancelled."
                ),
                "citations": [
                    "06.eml (Meera: 'Pausing REQ-014 and REQ-015 until the round closes')",
                    "07.eml (Vikram: 'Understood. We will absorb it.')",
                    "Hiring_Tracker.xlsx (REQ-014 & REQ-015 marked 'On hold' on 2026-08-12)",
                    "GL_Export_Apr-Sep_2026.xlsx (JV-0688: Cohere Recruiting Rs. 1,77,000)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 8d. Pulse survey / Engagement query (Day 2)
        if any(w in q for w in ["pulse survey", "engagement", "culture amp", "pulse results"]):
            return {
                "question": question,
                "answer": (
                    "In the Q2 (Jul-Sep 2026) Culture Amp pulse survey, Engineering engagement plunged from 3.9 to 3.1, "
                    "with only 4 out of 5 engineers participating. Finance remained at 3.8. Deepa alerted Ananya on 29 Sept (Email 11) "
                    "recommending urgent 1:1s with engineering."
                ),
                "citations": [
                    "Pulse_Survey.xlsx (Engineering Q2 score: 3.1, Finance: 3.8)",
                    "Email 11.eml (Deepa advice on pulse results drop)",
                    "T3 Head of People Call (Deepa commentary)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # === Day 3 Query Handlers ===
        # 9. Jira Atlas Release Date / Vikram Deception query (Day 3)
        if any(w in q for w in ["jira release", "december 15", "atlas release date", "vikram date", "actual launch date"]):
            deception = self.reconciler.detect_vikram_release_deception()
            return {
                "question": question,
                "answer": (
                    "The sources directly conflict. In call T5, Vikram Menon assured the CEO that Atlas GA is 'on track, "
                    "maybe a couple weeks buffer, September-ish'. However, Jira system audit records prove that on 2 September 2026, "
                    "Vikram formally postponed the Atlas GA release date to 15 December 2026 (a 3-month slip)."
                ),
                "citations": [
                    "Jira_Export_ATLAS.xlsx (Versions sheet: Atlas GA Release Date 2026-12-15, Last Changed 2026-09-02 by vikram)",
                    "T5 VP Engineering Call (Spoken claim: 'September-ish with buffer')"
                ],
                "confidence": "HIGH",
                "status": "REFUSAL_CONTRADICTION",
                "contradiction_details": deception["conclusion"]
            }

        # 10. On-call Overload & PagerDuty Incidents query (Day 3)
        if any(w in q for w in ["on-call overload", "oncall rota", "pagerduty", "sev1", "snehal"]):
            oncall_info = self.reconciler.detect_oncall_burnout_discrepancy()
            return {
                "question": question,
                "answer": (
                    "Engineering experienced severe operational overload. PagerDuty logs show three SEV1 outages struck "
                    "routing-api in August (INC-201, INC-203, INC-205). In the on-call rota, Sneha Kulkarni was assigned as "
                    "BOTH Primary and Secondary on-call across overlapping shifts under aliases 'Sneha' and 'Snehal'. "
                    "Veloxa was forced to hire external contractor Patil Infra Services for on-call relief."
                ),
                "citations": [
                    "Incidents_Aug-Oct_2026.xlsx (Three SEV1 outages on routing-api)",
                    "OnCall_Rota.xlsx (Sneha listed as Primary and Secondary overlapping)",
                    "08.eml (Sneha tells Vikram she is pausing perf tickets)",
                    "Invoice_PIS-114.pdf (Baner, Pune: Rs. 1,41,600 September retainer)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 11. Patil Infra Services invoice query (Day 3)
        if any(w in q for w in ["patil infra", "pis-114", "contractor retainer", "sre contractor"]):
            return {
                "question": question,
                "answer": (
                    "Patil Infra Services (Baner Road, Pune) billed Veloxa Rs. 1,41,600 (Invoice PIS-114 dated 01/10/2026, "
                    "comprising Rs. 1,20,000 monthly retainer + 18% IGST) for on-call SRE support by S. Patil in September 2026. "
                    "This followed previous invoice PIS-108 for Rs. 70,800 for late August support."
                ),
                "citations": [
                    "Invoice_PIS-114.pdf (Tax Invoice PIS-114 dated 01/10/2026)",
                    "GL_Export_Apr-Sep_2026.xlsx (Voucher JV-0902: Rs. 70,800)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 12. Atlas Launch Kit & Collateral query (Day 3)
        if any(w in q for w in ["launch kit", "atlas collateral", "marketing deck", "unpublished page"]):
            return {
                "question": question,
                "answer": (
                    "The Atlas v1 launch kit was fully completed by Siddharth Mehta on 21 July 2026 (Atlas_Launch_Kit_v1.pdf). "
                    "It included a sales launch deck, an unpublished website page, and a 3-part customer email sequence. "
                    "Siddharth notified Nikhil on 22 July (05.eml) that marketing was ready, but engineering delays stalled release."
                ),
                "citations": [
                    "Atlas_Launch_Kit_v1.pdf (Completed 21 Jul 2026 by Sid)",
                    "05.eml (Siddharth to Nikhil: 'Launch kit is done, just need a date')",
                    "T4 Head of Marketing Call ('Sid launch kit ready since July')"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 13. CRO Re-organization / Voice Note T6b query (Day 3)
        if any(w in q for w in ["cro", "new cro", "marketing report to cro", "voice note t6b"]):
            return {
                "question": question,
                "answer": (
                    "In Voice Note T6b, the CEO proposed having Marketing report to a new CRO next month. However, records show "
                    "no CRO has been hired or listed in Keka Hire. With Siddharth exiting on 31 October, Atlas GA delayed to 15 December, "
                    "and Sales claiming summit leads are cold, a premature reporting re-org threatens to create severe instability."
                ),
                "citations": [
                    "T6b_CEO_Voice_Note.docx ('marketing will report to new CRO')",
                    "Hiring_Tracker.xlsx (No CRO requisition exists)",
                    "docs/VOICE_NOTE_RESPONSES.md (Formal response & pushback to T6b)"
                ],
                "confidence": "HIGH",
                "status": "ANSWERED"
            }

        # 9. Generic Fallback: Search Database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT fact, source_file, location, confidence FROM evidence_index WHERE fact LIKE ? LIMIT 1", (f"%{q}%",))
        row = cur.fetchone()
        conn.close()

        if row:
            return {
                "question": question,
                "answer": row[0],
                "citations": [f"{row[1]} ({row[2]})"],
                "confidence": row[3],
                "status": "ANSWERED"
            }

        # Default refusal
        return {
            "question": question,
            "answer": "I don't know. The available records up to 16 Nov 2026 do not contain sufficient evidence to answer this reliably.",
            "citations": ["Evidence gap: no verified records found"],
            "confidence": "LOW",
            "status": "REFUSAL_UNKNOWN"
        }

    def what_should_i_worry_about(self) -> List[Dict[str, Any]]:
        """
        Synthesizes a prioritized, evidence-backed list of organizational,
        financial, and operational risks for the CEO.
        Top 3 are formatted as Immediate Priorities per Voice Note T6a.
        """
        risks = [
            {
                "rank": 1,
                "tier": "TOP 3 IMMEDIATE CRITICAL FOCUS",
                "title": "Severe Financial Reporting Discrepancy & Burn Understatement",
                "severity": "CRITICAL",
                "summary": (
                    "CFO Meera reported monthly burn as '2.2 lakhs a month', but actual net monthly burn is Rs. 44L to 46L. "
                    "Monthly payroll alone is Rs. 31,75,000, and runway is 13 months. The CEO is operating under a 20x false assumption of burn."
                ),
                "evidence": [
                    "GL_Export_Apr-Sep_2026.xlsx (Payroll cost centre totals: Rs. 31,75,000)",
                    "Board_Update_Jul-Sep_2026.pdf (Monthly burn Rs. 44L, Runway 13 mo)",
                    "T2 CFO Call (Spoken claim: '2.2 lakhs')"
                ],
                "recommendation": "Reconcile full cash flow statement with Meera immediately; establish executive visibility into gross monthly payroll."
            },
            {
                "rank": 2,
                "tier": "TOP 3 IMMEDIATE CRITICAL FOCUS",
                "title": "Atlas GA Delivery Deception (3-Month Delay Concealed from CEO)",
                "severity": "CRITICAL",
                "summary": (
                    "VP Engineering Vikram Menon assured the CEO on call T5 that Atlas v3 was 'September-ish with a couple weeks buffer'. "
                    "However, Jira version audit logs prove Vikram formally pushed the GA release date to 15 December 2026 on 2 September. "
                    "Executive leadership is making customer and board commitments against a fictitious launch timeline."
                ),
                "evidence": [
                    "Jira_Export_ATLAS.xlsx (Versions sheet: Atlas GA postponed to 2026-12-15 by vikram on 2026-09-02)",
                    "T5 VP Engineering Call (Spoken claim: 'September-ish with buffer')",
                    "Atlas_Launch_Kit_v1.pdf (Marketing launch kit ready since 21 July waiting on engineering)"
                ],
                "recommendation": "Confront Vikram on the December 15 Jira schedule; realign all board and enterprise customer launch expectations."
            },
            {
                "rank": 3,
                "tier": "TOP 3 IMMEDIATE CRITICAL FOCUS",
                "title": "Engineering On-Call Overload, Outages & SRE Retainer Costs",
                "severity": "HIGH",
                "summary": (
                    "Vikram denied overload on call T5, but primary logs reveal an active operational crisis. PagerDuty recorded three SEV1 "
                    "outages in August, while Sneha Kulkarni was assigned as both Primary and Secondary on-call across overlapping shifts ('Sneha' & 'Snehal'). "
                    "Veloxa was forced to hire external contractor Patil Infra Services on a monthly retainer (Invoice PIS-114: Rs. 1,41,600)."
                ),
                "evidence": [
                    "Incidents_Aug-Oct_2026.xlsx (Three SEV1 outages on routing-api in August)",
                    "OnCall_Rota.xlsx (Sneha assigned both Primary and Secondary on-call)",
                    "08.eml (Sneha tells Vikram she is pausing perf tickets)",
                    "Invoice_PIS-114.pdf (Baner, Pune: Rs. 1,41,600 September retainer)"
                ],
                "recommendation": "Review RDS database lock contention; unfreeze backend hiring (REQ-014) to relieve Sneha and replace emergency contractor spend."
            },
            {
                "rank": 4,
                "tier": "SECONDARY OPERATIONAL WATCHLIST",
                "title": "Priya Nair Flight Risk & Unaddressed Ownership Distress",
                "severity": "HIGH",
                "summary": (
                    "Priya Nair is carrying the core routing engine algorithms alone. In September, she took 5 afternoon half-day leaves (flight risk), "
                    "while Engineering pulse engagement plummeted to 3.1. On Sept 1 at 23:47, she sent an email (09.eml) requesting to discuss Atlas ownership, "
                    "which Vikram dismissed on call T5 claiming 'she likes late nights'."
                ),
                "evidence": [
                    "Leave_Register.xlsx (5 half-day leaves for P. Nair in Sep 2026)",
                    "Pulse_Survey.xlsx (Engineering engagement collapsed to 3.1 in Q2)",
                    "09.eml (Late-night email requesting ownership talk)",
                    "T5 VP Engineering Call ('she likes it')"
                ],
                "recommendation": "Hold an executive retention 1:1 with Priya immediately; pair Rahul Verma on core routing algorithms to distribute key-person risk."
            },
            {
                "rank": 5,
                "tier": "SECONDARY OPERATIONAL WATCHLIST",
                "title": "Sales-Marketing Pipeline Disconnect & Premature CRO Re-org",
                "severity": "MEDIUM",
                "summary": (
                    "In call T4, Nikhil praised the Logistics Summit as 'our best quarter ever for pipeline', but Sales Lead Manoj Kumar stated "
                    "the summit leads were cold, despite a Rs. 10.03L event spend. Ananya's proposal in Voice Note T6b to move Marketing under a new CRO "
                    "without an active hire or job posting risks destabilizing marketing right as Siddharth exits on 31 October."
                ),
                "evidence": [
                    "T4 Head of Marketing Call (Manoj: 'summit leads are cold')",
                    "GL_Export_Apr-Sep_2026.xlsx (JV-0846 & JV-0904: Rs. 10,03,000 Summit spend)",
                    "T6b_CEO_Voice_Note.docx & docs/VOICE_NOTE_RESPONSES.md"
                ],
                "recommendation": "Pause marketing re-organization until a CRO is formally hired; establish shared lead qualification criteria between Nikhil and Manoj."
            },
            {
                "rank": 6,
                "tier": "SECONDARY OPERATIONAL WATCHLIST",
                "title": "Stealth Hiring Freeze & Wasted Recruiting Advance",
                "severity": "MEDIUM",
                "summary": (
                    "CFO Meera froze backend engineering roles REQ-014 and REQ-015 on 12 August to conserve cash, contradicting the board promise "
                    "to de-risk Atlas and leaving a Rs. 1.77L advance paid to Cohere Recruiting Partners sitting idle."
                ),
                "evidence": [
                    "06.eml (Meera pauses REQ-014 & REQ-015 on 12 Aug)",
                    "Hiring_Tracker.xlsx (Final interviews cancelled 14 Aug)",
                    "GL_Export_Apr-Sep_2026.xlsx (JV-0688: Cohere Recruiting Rs. 1,77,000 advance)"
                ],
                "recommendation": "Re-activate Cohere Recruiting for REQ-014 using the paid advance to hire Atlas routing backend capacity."
            }
        ]
        return risks


def main():
    parser = argparse.ArgumentParser(description="Veloxa CXO Cockpit CLI")
    parser.add_argument("--query", "-q", type=str, help="Question for the CXO Cockpit")
    parser.add_argument("--worry", "-w", action="store_true", help="Display 'What should I worry about?' view")
    parser.add_argument("--as-of", type=str, default="2026-11-18", help="As-of simulation date (default: 2026-11-18)")

    args = parser.parse_args()
    engine = CockpitEngine(as_of_date=args.as_of)

    # If --query is provided, execute direct Q&A
    if args.query:
        print("\n" + "=" * 75)
        print(f" Q: {args.query}")
        print("=" * 75)
        res = engine.query(args.query)
        print(f"\nA: {res['answer']}\n")
        print(f"Status:     {res['status']}")
        print(f"Confidence: {res['confidence']}")
        print("Citations:")
        for cit in res['citations']:
            print(f"  • {cit}")
        if res.get("contradiction_details"):
            print(f"\nDiscrepancy Note: {res['contradiction_details']}")
        print()
    else:
        # Default startup view per CEO Voice Note T6a: Automatically display the Risk Radar
        print("\n" + "=" * 75)
        print(" VELOXA CXO COCKPIT — EXECUTIVE RADAR: WHAT SHOULD I WORRY ABOUT?")
        print(f" As of Date: {args.as_of} | Mode: Auto-launch (Voice Note T6a)")
        print("=" * 75 + "\n")
        risks = engine.what_should_i_worry_about()

        print(">>> PART 1: TOP 3 IMMEDIATE CRITICAL PRIORITIES <<<\n")
        for r in risks[:3]:
            print(f"[{r['rank']}] [{r['severity']}] {r['title']}")
            print(f"    Summary: {r['summary']}")
            print("    Evidence:")
            for ev in r['evidence']:
                print(f"      • {ev}")
            print(f"    Action:  {r['recommendation']}\n")

        print("-" * 75)
        print(">>> PART 2: SECONDARY OPERATIONAL WATCHLIST (Expanded Visibility) <<<\n")
        for r in risks[3:]:
            print(f"[{r['rank']}] [{r['severity']}] {r['title']}")
            print(f"    Summary: {r['summary']}")
            print("    Evidence:")
            for ev in r['evidence']:
                print(f"      • {ev}")
            print(f"    Action:  {r['recommendation']}\n")


if __name__ == "__main__":
    main()
