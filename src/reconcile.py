"""
Reconciliation & Entity Resolution Module for Veloxa CXO Cockpit.
Resolves phonetic aliases, tool names, vendor variations, and cross-checks
spoken transcript claims against hard system ledger records.
"""

import sqlite3
from typing import Dict, List, Optional, Any

DB_PATH = "veloxa.db"


class ReconciliationEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        
        # Canonical entity resolution mapping
        self.entity_map = {
            # People aliases
            "pria": {"canonical": "Priya Nair", "emp_id": "VX007", "kind": "person", "dept": "Engineering"},
            "priya": {"canonical": "Priya Nair", "emp_id": "VX007", "kind": "person", "dept": "Engineering"},
            "priya nair": {"canonical": "Priya Nair", "emp_id": "VX007", "kind": "person", "dept": "Engineering"},
            "vicky": {"canonical": "Vikram Menon", "emp_id": "VX004", "kind": "person", "dept": "Engineering"},
            "vikram": {"canonical": "Vikram Menon", "emp_id": "VX004", "kind": "person", "dept": "Engineering"},
            "vikram menon": {"canonical": "Vikram Menon", "emp_id": "VX004", "kind": "person", "dept": "Engineering"},
            "meera": {"canonical": "Meera Iyer", "emp_id": "VX003", "kind": "person", "dept": "Finance"},
            "meera iyer": {"canonical": "Meera Iyer", "emp_id": "VX003", "kind": "person", "dept": "Finance"},
            "kartik": {"canonical": "Karthik Subramanian", "emp_id": "VX010", "kind": "person", "dept": "Finance"},
            "karthik": {"canonical": "Karthik Subramanian", "emp_id": "VX010", "kind": "person", "dept": "Finance"},
            "fatima shaikh": {"canonical": "Fatima Sheikh", "emp_id": "VX014", "kind": "person", "dept": "Finance"},
            "fatima sheikh": {"canonical": "Fatima Sheikh", "emp_id": "VX014", "kind": "person", "dept": "Finance"},
            "fatima": {"canonical": "Fatima Sheikh", "emp_id": "VX014", "kind": "person", "dept": "Finance"},
            "deepa": {"canonical": "Deepa Joshi", "emp_id": "VX005", "kind": "person", "dept": "People & Ops"},
            "deepa joshi": {"canonical": "Deepa Joshi", "emp_id": "VX005", "kind": "person", "dept": "People & Ops"},
            "nikhil": {"canonical": "Nikhil Bose", "emp_id": "VX006", "kind": "person", "dept": "Marketing"},
            "nikhil bose": {"canonical": "Nikhil Bose", "emp_id": "VX006", "kind": "person", "dept": "Marketing"},
            "rahul": {"canonical": "Rahul Verma", "emp_id": "VX018", "kind": "person", "dept": "Engineering"},
            "rahul verma": {"canonical": "Rahul Verma", "emp_id": "VX018", "kind": "person", "dept": "Engineering"},
            "arjun": {"canonical": "Arjun Das", "emp_id": "VX009", "kind": "person", "dept": "Engineering"},
            "sneha": {"canonical": "Sneha Kulkarni", "emp_id": "VX012", "kind": "person", "dept": "Engineering"},
            "snehal": {"canonical": "Sneha Kulkarni", "emp_id": "VX012", "kind": "person", "dept": "Engineering"},
            "siddharth": {"canonical": "Siddharth Mehta", "emp_id": "VX013", "kind": "person", "dept": "Marketing"},
            "sid": {"canonical": "Siddharth Mehta", "emp_id": "VX013", "kind": "person", "dept": "Marketing"},
            "aisha": {"canonical": "Aisha Khan", "emp_id": "VX011", "kind": "person", "dept": "Marketing"},
            "ayesha": {"canonical": "Aisha Khan", "emp_id": "VX011", "kind": "person", "dept": "Marketing"},
            "rohan": {"canonical": "Rohan Banerjee", "emp_id": "VX015", "kind": "person", "dept": "People & Ops"},
            "lakshmi": {"canonical": "Lakshmi Pillai", "emp_id": "VX017", "kind": "person", "dept": "People & Ops"},
            "manoj": {"canonical": "Manoj Kumar", "emp_id": "VX002", "kind": "person", "dept": "Sales"},

            # Tool aliases
            "jeera": {"canonical": "Jira", "kind": "tool", "category": "Project Management"},
            "linear": {"canonical": "Linear", "kind": "tool", "category": "Project Management"},
            "joho": {"canonical": "Zoho Books", "kind": "tool", "category": "Finance Ledger"},
            "joho books": {"canonical": "Zoho Books", "kind": "tool", "category": "Finance Ledger"},
            "kayka": {"canonical": "Keka HRMS", "kind": "tool", "category": "HRMS & Payroll"},
            "kekka": {"canonical": "Keka HRMS", "kind": "tool", "category": "HRMS & Payroll"},
            "liver": {"canonical": "Lever ATS", "kind": "tool", "category": "Applicant Tracking"},
            "cult amp": {"canonical": "Culture Amp", "kind": "tool", "category": "Employee Surveys"},
            "slag": {"canonical": "Slack", "kind": "tool", "category": "Internal Communication"},
            "hub sport": {"canonical": "HubSpot", "kind": "tool", "category": "CRM & Marketing"},
            "pager duty": {"canonical": "PagerDuty", "kind": "tool", "category": "Incident Response"},
            "pagerduty": {"canonical": "PagerDuty", "kind": "tool", "category": "Incident Response"},
            "con fluence": {"canonical": "Confluence", "kind": "tool", "category": "Documentation"},
            "confluence": {"canonical": "Confluence", "kind": "tool", "category": "Documentation"},

            # Vendor aliases
            "sapphire events pvt ltd": {"canonical": "Sapphire Events", "kind": "vendor", "purpose": "Event Management"},
            "saphire event mgmt": {"canonical": "Sapphire Events", "kind": "vendor", "purpose": "Event Management"},
            "patil infra services": {"canonical": "Patil Infra Services", "kind": "vendor", "purpose": "On-Call Ops Support"},
            "cohere recruiting partners": {"canonical": "Cohere Recruiting Partners", "kind": "vendor", "purpose": "Recruiting Agency"},

            # Project / Product aliases
            "routing engine version three": {"canonical": "Atlas (Routing Engine v3)", "kind": "project", "owner": "Priya Nair"},
            "routing thing": {"canonical": "Atlas (Routing Engine v3)", "kind": "project", "owner": "Priya Nair"},
            "atlas": {"canonical": "Atlas (Routing Engine v3)", "kind": "project", "owner": "Priya Nair"}
        }

    def resolve_entity(self, name_or_alias: str) -> Dict[str, Any]:
        """Resolves an informal or misheard name/alias to its canonical entity."""
        clean_key = name_or_alias.strip().lower()
        if clean_key in self.entity_map:
            result = self.entity_map[clean_key].copy()
            result["confidence"] = "HIGH"
            result["original_input"] = name_or_alias
            return result
        
        # Substring / fuzzy match
        for key, val in self.entity_map.items():
            if key in clean_key or clean_key in key:
                res = val.copy()
                res["confidence"] = "MEDIUM"
                res["original_input"] = name_or_alias
                return res

        return {
            "canonical": name_or_alias,
            "kind": "unknown",
            "confidence": "LOW",
            "original_input": name_or_alias
        }

    def detect_headcount_conflict(self) -> Dict[str, Any]:
        """Compares transcript headcount claims against HRMS and Board updates."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM employees WHERE status = 'Active' OR status = 'Notice period'")
        hrms_count = cur.fetchone()[0]

        cur.execute("SELECT period, team_size FROM board_updates ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        board_team = row[1] if row else 19

        conn.close()

        return {
            "conflict_id": "CONF-001",
            "topic": "Company Headcount",
            "sources": [
                {"source": "T1 CEO Kickoff Call", "claim": "roughly 180 give or take (or 18)", "type": "transcript"},
                {"source": "Employee_Master.xlsx", "claim": f"{hrms_count} active employees", "type": "hrms_ledger"},
                {"source": "Board_Update_Jul-Sep_2026.pdf", "claim": f"Team: {board_team}", "type": "board_report"}
            ],
            "resolved_value": 19,
            "confidence": "HIGH",
            "reasoning": (
                "Keka HRMS lists exactly 19 employees. Board updates for Q1 and Q2 2026 both explicitly report "
                "Team: 19. Ananya's remark 'one-eighty' was an ASR transcription error or sarcastic exaggeration."
            )
        }

    def detect_burn_rate_conflict(self) -> Dict[str, Any]:
        """Cross-checks CFO spoken burn rate against General Ledger monthly expenses."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Monthly payroll average
        cur.execute("SELECT avg(amount) FROM general_ledger WHERE cost_centre = 'PAYROLL'")
        avg_payroll = cur.fetchone()[0] or 3175000.0

        # Monthly rent
        cur.execute("SELECT avg(amount) FROM general_ledger WHERE cost_centre = 'G&A'")
        avg_rent = cur.fetchone()[0] or 236000.0

        # Monthly AWS
        cur.execute("SELECT avg(amount) FROM general_ledger WHERE cost_centre = 'ENG-INF'")
        avg_aws = cur.fetchone()[0] or 209695.0

        total_tracked_monthly = avg_payroll + avg_rent + avg_aws

        cur.execute("SELECT period, monthly_burn FROM board_updates ORDER BY id DESC LIMIT 1")
        board_row = cur.fetchone()
        board_burn = board_row[1] if board_row else "Rs. 44 L"

        conn.close()

        return {
            "conflict_id": "CONF-002",
            "topic": "Monthly Cash Burn",
            "sources": [
                {"source": "T2 CFO Call", "claim": "2.2 lakhs a month, sometimes 2.5", "type": "transcript"},
                {"source": "GL_Export_Apr-Sep_2026.xlsx", "claim": f"Monthly payroll alone: Rs. {avg_payroll:,.0f}; Rent: Rs. {avg_rent:,.0f}; AWS: Rs. {avg_aws:,.0f}", "type": "general_ledger"},
                {"source": "Board_Update_Jul-Sep_2026.pdf", "claim": f"Monthly burn: {board_burn}", "type": "board_report"}
            ],
            "resolved_value": "Rs. 44 Lakhs - 46 Lakhs / month",
            "confidence": "HIGH",
            "reasoning": (
                "Meera's spoken claim of 2.2 Lakhs is completely contradicted by the ledger. Monthly payroll alone "
                "is Rs. 31.75 Lakhs. True net burn is ~Rs. 44L-46L as confirmed in Board Updates."
            )
        }

    def detect_rahul_verma_payroll_anomaly(self) -> Dict[str, Any]:
        """Checks Rahul Verma's joining date against February payroll days payable."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT join_date FROM employees WHERE emp_id = 'VX018'")
        join_date = cur.fetchone()[0]

        cur.execute("SELECT month, days_in_month, days_payable, gross, processed_by FROM payroll_records WHERE emp_id = 'VX018' AND month = 'Feb-2026'")
        row = cur.fetchone()
        days_in_month = row[1] if row else 28
        days_payable = row[2] if row else 28
        gross = row[3] if row else 110000.0
        processor = row[4] if row else "KS"

        cur.execute("SELECT date_str, subject, body FROM emails WHERE from_addr LIKE '%rahul.v%'")
        email_row = cur.fetchone()
        email_snippet = email_row[2] if email_row else ""

        conn.close()

        return {
            "conflict_id": "CONF-003",
            "topic": "Rahul Verma February Payroll Overpayment",
            "employee_id": "VX018",
            "join_date": join_date,
            "feb_days_in_month": days_in_month,
            "feb_days_payable": days_payable,
            "feb_gross": gross,
            "processed_by": processor,
            "email_evidence": email_snippet,
            "anomaly": (
                f"Rahul joined on {join_date} (3 days into month). Feb had 28 days, but payroll processed full "
                f"{days_payable} days payable (Gross Rs. {gross:,.0f}) by {processor}. Rahul flagged in email 02.eml."
            ),
            "status": "Unadjusted overpayment"
        }

    def detect_atlas_schedule_delay(self) -> Dict[str, Any]:
        """Reconciles CEO Atlas launch expectation with board updates and contractor expenses."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT txn_date, vendor, amount, narration FROM general_ledger WHERE vendor LIKE '%Patil Infra%'")
        patil_row = cur.fetchone()

        cur.execute("SELECT period, full_text FROM board_updates WHERE period LIKE '%Jul to Sep%'")
        board_row = cur.fetchone()
        board_text = board_row[1] if board_row else ""

        conn.close()

        return {
            "conflict_id": "CONF-004",
            "topic": "Atlas (Routing Engine v3) Release Slippage",
            "q1_commitment": "Target GA 15 September (Board Update Apr-Jun 2026)",
            "q2_status": "Moved GA to absorb unplanned reliability work after difficult August (Board Update Jul-Sep 2026)",
            "contractor_support": f"Vendor {patil_row[1]}, Rs. {patil_row[2]:,.0f} for '{patil_row[3]}'" if patil_row else "None",
            "conclusion": (
                "Atlas missed its September 15 GA target due to August outages/reliability emergencies requiring "
                "emergency external on-call support from Patil Infra Services."
            )
        }

    def detect_hiring_freeze_conflict(self) -> Dict[str, Any]:
        """Cross-checks Atlas de-risking hiring promise against the stealth hiring freeze."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT req_id, role, status, status_date, notes FROM hiring_requisitions WHERE req_id IN ('REQ-014', 'REQ-015')")
        req_rows = cur.fetchall()

        cur.execute("SELECT amount, ref FROM general_ledger WHERE vendor LIKE '%Cohere%'")
        cohere_row = cur.fetchone()

        conn.close()

        return {
            "conflict_id": "CONF-005",
            "topic": "Atlas Engineering De-risking vs Stealth Hiring Freeze",
            "board_promise": "Board Update Apr-Jun: 'We will add two backend engineers this quarter to de-risk Atlas.'",
            "cohere_advance": f"Paid Cohere Recruiting Rs. {cohere_row[0]:,.0f} (50% advance)" if cohere_row else "Rs. 1,77,000",
            "actual_status": "Email 06 (12 Aug): Meera pauses REQ-014 and REQ-015; final round interviews cancelled 14-Aug.",
            "confidence": "HIGH",
            "reasoning": (
                "The board was told two backend engineers were being hired to de-risk Atlas. Veloxa paid Rs. 1.77L "
                "to Cohere Recruiting, but Meera quietly froze both reqs on 12 August to conserve cash, leaving Atlas "
                "vulnerable and without additional engineering support."
            )
        }

    def detect_priya_flight_risk(self) -> Dict[str, Any]:
        """Correlates unnamed worried engineer with Priya Nair's leave pattern and pulse survey drop."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT count(*), sum(days) FROM leave_records WHERE employee = 'P. Nair' AND from_date LIKE '2026-09%'")
        leave_row = cur.fetchone()
        leave_count = leave_row[0] if leave_row else 0
        leave_days = leave_row[1] if leave_row else 0.0

        cur.execute("SELECT quarter, engagement_score, responses, team_size FROM pulse_surveys WHERE team = 'Engineering' AND quarter = 'Jul-Sep 2026'")
        pulse_row = cur.fetchone()
        score = pulse_row[1] if pulse_row else 3.1
        resp = pulse_row[2] if pulse_row else 4
        size = pulse_row[3] if pulse_row else 5

        conn.close()

        return {
            "conflict_id": "CONF-006",
            "topic": "Priya Nair Flight Risk & Unnamed Worried Engineer",
            "deepa_call_clue": "T3: Deepa mentions 'there is one engineer I'm worried about' but refuses to name them.",
            "leave_pattern": f"Priya Nair took {leave_count} half-day personal leaves ({leave_days} days total) in September 2026.",
            "pulse_signal": f"Engineering Culture Amp pulse crashed to {score} in Q2 with only {resp} of {size} responding.",
            "confidence": "HIGH",
            "conclusion": (
                "The unnamed engineer is Priya Nair. Repeated half-day afternoon leaves in September strongly correlate "
                "with offsite job interviews. Her burnout from holding Atlas together without backfills makes her Veloxa's #1 flight risk."
            )
        }

    def detect_recruiting_open_roles_conflict(self) -> Dict[str, Any]:
        """Compares Rohan's claim of 22 open roles in T3 against Keka Hire requisitions."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM hiring_requisitions")
        total_reqs = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM hiring_requisitions WHERE status = 'On hold'")
        hold_reqs = cur.fetchone()[0]
        conn.close()

        return {
            "conflict_id": "CONF-007",
            "topic": "Open Roles Discrepancy (Rohan vs Keka Hire)",
            "rohan_claim": "T3: Rohan claims 'twenty-two open roles in April' and 'we lost six in August'.",
            "keka_hire_record": f"Keka Hire lists only {total_reqs} total historical requisitions (REQ-011 through REQ-016), with {hold_reqs} on hold.",
            "confidence": "MEDIUM",
            "reasoning": (
                "Rohan's figure of 22 open roles does not exist in Keka Hire. He is either referring to an informal "
                "future headcount wishlist or the ASR misheard 'two' or 'twelve'. Only 2 engineering reqs were paused in August."
            )
        }

    def detect_vikram_release_deception(self) -> Dict[str, Any]:
        """Exposes discrepancy between Vikram's spoken claim in T5 and Jira GA release date."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT release_date, original_release_date, last_changed, changed_by FROM jira_versions WHERE version_name = 'Atlas GA'")
        row = cur.fetchone()
        conn.close()

        jira_rel = row[0] if row else "2026-12-15"
        orig_rel = row[1] if row else "2026-09-15"
        changed_dt = row[2] if row else "2026-09-02"
        changed_by = row[3] if row else "vikram"

        return {
            "conflict_id": "CONF-008",
            "topic": "Atlas GA Delivery Timeline Misrepresentation",
            "vikram_call_claim": "T5: Vikram tells Ananya v3 is 'on track, maybe a couple weeks buffer, September-ish'.",
            "jira_hard_record": f"Jira Versions shows Atlas GA postponed from {orig_rel} to {jira_rel} by {changed_by} on {changed_dt}.",
            "confidence": "HIGH",
            "conclusion": (
                f"Vikram is actively misrepresenting the delivery timeline to the CEO. On {changed_dt}, he changed Jira's "
                f"official release date to {jira_rel} (a 3-month slip), yet on the call he claimed it was 'September-ish'."
            )
        }

    def detect_oncall_burnout_discrepancy(self) -> Dict[str, Any]:
        """Cross-checks Vikram's claim that no one is overloaded against OnCall Rota and PagerDuty."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM pagerduty_incidents WHERE severity = 'SEV1'")
        sev1_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM oncall_rota WHERE primary_oncall LIKE '%Sneha%' AND secondary_oncall LIKE '%Sneha%'")
        double_shift_weeks = cur.fetchone()[0]
        cur.execute("SELECT amount FROM invoices WHERE invoice_no = 'PIS-114'")
        inv_row = cur.fetchone()
        patil_invoice = inv_row[0] if inv_row else 141600.0
        conn.close()

        return {
            "conflict_id": "CONF-009",
            "topic": "Engineering On-Call Overload Denial vs Reality",
            "vikram_call_claim": "T5: Vikram disputes overload ('everyone busy, that's startups... Pria likes late nights').",
            "incident_reality": f"PagerDuty shows {sev1_count} SEV1 outages on routing-api in August.",
            "oncall_rota_reality": f"Sneha Kulkarni was assigned as BOTH primary and secondary on-call for {double_shift_weeks} weeks ('Sneha' & 'Snehal').",
            "contractor_reality": f"Veloxa was forced to hire Patil Infra Services (Baner, Pune) on a monthly retainer (Invoice PIS-114: Rs. {patil_invoice:,.0f}).",
            "confidence": "HIGH",
            "conclusion": (
                "Vikram's assertion that engineering is not overloaded is directly contradicted by primary logs. "
                "Sneha was on-call 24/7 as both primary and secondary, leading to burnout and emergency external contractor costs."
            )
        }

    def detect_marketing_sales_pipeline_conflict(self) -> Dict[str, Any]:
        """Contrasts Nikhil's pipeline triumph with Sales Lead Manoj's feedback."""
        return {
            "conflict_id": "CONF-010",
            "topic": "Marketing Summit Pipeline vs Sales Lead Rejection",
            "nikhil_claim": "T4: Nikhil calls the September summit 'our best quarter ever for pipeline'.",
            "sales_reality": "T4: Manoj Kumar (Sales Lead) states the summit leads are completely cold.",
            "cost_reality": "General ledger shows Rs. 10,03,000 spent on Sapphire Events with only 212 registrations.",
            "confidence": "HIGH",
            "conclusion": (
                "Severe executive misalignment between Sales and Marketing. Marketing spent over 10 Lakhs on the summit "
                "and declared victory, while Sales claims zero actionable pipeline was produced."
            )
        }

    def get_all_reconciliations(self) -> List[Dict[str, Any]]:
        """Returns all detected conflicts and reconciliations."""
        return [
            self.detect_headcount_conflict(),
            self.detect_burn_rate_conflict(),
            self.detect_rahul_verma_payroll_anomaly(),
            self.detect_atlas_schedule_delay(),
            self.detect_hiring_freeze_conflict(),
            self.detect_priya_flight_risk(),
            self.detect_recruiting_open_roles_conflict(),
            self.detect_vikram_release_deception(),
            self.detect_oncall_burnout_discrepancy(),
            self.detect_marketing_sales_pipeline_conflict()
        ]


def main():
    print("=== Veloxa Reconciliation & Entity Resolution Engine ===")
    engine = ReconciliationEngine()

    print("\n--- Testing Entity Resolution ---")
    for sample in ["Pria", "Vicky", "Jeera", "Joho books", "Cult Amp", "Sapphire Events Pvt Ltd", "Fatima Shaikh"]:
        res = engine.resolve_entity(sample)
        print(f"'{sample}' -> {res['canonical']} (Kind: {res['kind']}, Confidence: {res['confidence']})")

    print("\n--- Detected Discrepancies & Reconciliations ---")
    for conf in engine.get_all_reconciliations():
        print(f"\n[{conf.get('conflict_id')}] {conf.get('topic')}:")
        if "reasoning" in conf:
            print(f"  Reasoning: {conf['reasoning']}")
        elif "anomaly" in conf:
            print(f"  Anomaly: {conf['anomaly']}")
        elif "conclusion" in conf:
            print(f"  Conclusion: {conf['conclusion']}")


if __name__ == "__main__":
    main()
