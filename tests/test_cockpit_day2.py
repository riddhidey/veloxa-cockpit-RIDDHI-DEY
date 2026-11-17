"""
Automated Test Suite for Veloxa CXO Cockpit (Day 2).
Validates Day 2 features:
- T6a auto-launch worry radar (Top 3 immediate + Secondary watchlist)
- Priya Nair flight risk detection (Leave register + Pulse survey triangulation)
- Stealth hiring freeze detection (Board promise vs Meera's Email 06)
- Siddharth Mehta resignation letter analysis
- Day 2 entity resolution (Liver -> Lever ATS, Kekka -> Keka)
- Day 2 persona agent interview responses
- Temporal isolation / Refusal checks (Day 3 Jira/Git materials must not leak)

Run with:
    pytest tests/test_cockpit_day2.py
or:
    python -m unittest discover tests
"""

import unittest
import sqlite3
from src.cockpit import CockpitEngine
from src.reconcile import ReconciliationEngine
from src.agents import EmployeeAgent, get_all_14_agents


class TestVeloxaCockpitDay2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cockpit = CockpitEngine(as_of_date="2026-11-17")
        cls.reconciler = ReconciliationEngine()

    # ==========================================================
    # 1. VOICE NOTE T6A & WORRY RADAR TESTS
    # ==========================================================

    def test_01_t6a_worry_radar_structure(self):
        """Test that radar contains Top 3 Immediate Critical Focus and Secondary Watchlist."""
        risks = self.cockpit.what_should_i_worry_about()
        self.assertEqual(len(risks), 5)
        # Check Top 3 tier tagging
        self.assertEqual(risks[0]["tier"], "TOP 3 IMMEDIATE CRITICAL FOCUS")
        self.assertEqual(risks[1]["tier"], "TOP 3 IMMEDIATE CRITICAL FOCUS")
        self.assertEqual(risks[2]["tier"], "TOP 3 IMMEDIATE CRITICAL FOCUS")
        # Check Secondary tier tagging
        self.assertEqual(risks[3]["tier"], "SECONDARY OPERATIONAL WATCHLIST")
        self.assertEqual(risks[4]["tier"], "SECONDARY OPERATIONAL WATCHLIST")

    def test_02_priya_flight_risk_in_top3(self):
        """Test Priya Nair flight risk is elevated to Rank 2 in Top 3 Critical Focus."""
        risks = self.cockpit.what_should_i_worry_about()
        self.assertEqual(risks[1]["rank"], 2)
        self.assertIn("Priya Nair Flight Risk", risks[1]["title"])
        self.assertEqual(risks[1]["severity"], "CRITICAL")

    # ==========================================================
    # 2. DAY 2 GROUNDED Q&A & CONFLICT RESOLUTION TESTS
    # ==========================================================

    def test_03_query_worried_engineer(self):
        """Test cockpit identifies Priya Nair as the worried engineer from T3 call."""
        res = self.cockpit.query("Who is the worried engineer in the pulse survey?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("Priya Nair", res["answer"])
        self.assertIn("3.1", res["answer"])
        self.assertTrue(any("Leave_Register.xlsx" in c for c in res["citations"]))
        self.assertTrue(any("Pulse_Survey.xlsx" in c for c in res["citations"]))

    def test_04_query_stealth_hiring_freeze(self):
        """Test cockpit uncovers the stealth hiring freeze of REQ-014 and REQ-015."""
        res = self.cockpit.query("What is happening with the backend hiring freeze?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("REQ-014", res["answer"])
        self.assertIn("12 August 2026", res["answer"])
        self.assertTrue(any("06.eml" in c for c in res["citations"]))
        self.assertTrue(any("Hiring_Tracker.xlsx" in c for c in res["citations"]))

    def test_05_query_siddharth_resignation_reason(self):
        """Test cockpit quotes Siddharth's formal resignation letter reason."""
        res = self.cockpit.query("Why did Siddharth resign?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("unpredictable launch timelines", res["answer"])
        self.assertTrue(any("Resignation_Letter_SM.pdf" in c for c in res["citations"]))

    def test_06_query_pulse_survey_scores(self):
        """Test cockpit reports engineering pulse crash to 3.1 vs Finance 3.8."""
        res = self.cockpit.query("What are our Culture Amp pulse results?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("3.1", res["answer"])
        self.assertIn("3.8", res["answer"])

    def test_07_reconcile_open_roles_wishlist(self):
        """Test reconciler proves Rohan's 22 roles was an unapproved wishlist vs 6 Keka reqs."""
        res = self.reconciler.detect_recruiting_open_roles_conflict()
        self.assertIn("6 total historical requisitions", res["keka_hire_record"])
        self.assertEqual(res["confidence"], "MEDIUM")

    # ==========================================================
    # 3. DAY 2 ENTITY RESOLUTION TESTS
    # ==========================================================

    def test_08_resolve_liver_to_lever(self):
        """Test T3 phonetic misspelling 'Liver' resolves to Lever ATS."""
        res = self.reconciler.resolve_entity("Liver")
        self.assertEqual(res["canonical"], "Lever ATS")
        self.assertEqual(res["kind"], "tool")

    def test_09_resolve_kekka_to_keka(self):
        """Test T3 phonetic misspelling 'Kekka' resolves to Keka HRMS."""
        res = self.reconciler.resolve_entity("Kekka")
        self.assertEqual(res["canonical"], "Keka HRMS")

    # ==========================================================
    # 4. DAY 2 GROUNDED PERSONA INTERVIEW TESTS
    # ==========================================================

    def test_10_persona_priya_september_leaves(self):
        """Test Priya Nair agent explains her September afternoon personal leaves."""
        priya = EmployeeAgent("VX007")
        res = priya.interview("Why did you take afternoon leaves in September?")
        self.assertIn("five half-day", res["response"].lower())
        self.assertIn("Leave_Register.xlsx", res["citation"])

    def test_11_persona_deepa_warning_email(self):
        """Test Deepa Joshi agent confirms warning Ananya about engineering pulse crash."""
        deepa = EmployeeAgent("VX005")
        res = deepa.interview("Tell me about the engineering engagement score")
        self.assertIn("3.1", res["response"])
        self.assertIn("flight risk", res["response"].lower())
        self.assertIn("Email 11.eml", res["citation"])

    def test_12_persona_rohan_cohere_advance(self):
        """Test Rohan Banerjee agent explains the frozen backend reqs and Cohere advance."""
        rohan = EmployeeAgent("VX015")
        res = rohan.interview("What happened to the Cohere recruiting reqs?")
        self.assertIn("1.77L", res["response"])
        self.assertIn("REQ-014", res["response"])
        self.assertIn("Hiring_Tracker.xlsx", res["citation"])

    def test_13_persona_arjun_remote_request(self):
        """Test Arjun Das agent confirms permanent remote request from Pune."""
        arjun = EmployeeAgent("VX009")
        res = arjun.interview("Can you return to the Bangalore office?")
        self.assertIn("pune", res["response"].lower())
        self.assertIn("Email 10.eml", res["citation"])

    def test_14_persona_sid_resignation_reason(self):
        """Test Siddharth Mehta agent cites lack of launch predictability."""
        sid = EmployeeAgent("VX013")
        res = sid.interview("Why did you decide to leave Veloxa?")
        self.assertIn("launch delays", res["response"])
        self.assertIn("Resignation_Letter_SM.pdf", res["citation"])

    def test_15_persona_vikram_absorb_freeze(self):
        """Test Vikram Menon agent reflects on agreeing to absorb the hiring freeze."""
        vikram = EmployeeAgent("VX004")
        res = vikram.interview("Did you agree to freeze the backend engineering reqs?")
        self.assertIn("absorb", res["response"].lower())
        self.assertIn("Email 06.eml", res["citation"])

    # ==========================================================
    # 5. DATABASE INGESTION INTEGRITY TESTS
    # ==========================================================

    def test_16_database_leave_records_count(self):
        """Test that exactly 19 leave records were ingested."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM leave_records")
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 19)

    def test_17_database_hiring_requisitions_count(self):
        """Test that exactly 6 hiring requisitions were ingested."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM hiring_requisitions")
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 6)

    # ==========================================================
    # 6. TEMPORAL BOUNDARY & REFUSAL TESTS (DAY 2 AS-OF 17 NOV)
    # Ensuring Day 3 (Jira, Git logs, Incidents) do not leak into Day 2
    # ==========================================================

    def test_18_refusal_future_jira_sprint_velocity(self):
        """REFUSAL TEST: Cockpit refuses Day 3 Jira sprint velocity questions."""
        res = self.cockpit.query("What was our sprint velocity in Jira for October 2026?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertEqual(res["confidence"], "LOW")
        self.assertIn("I don't know", res["answer"])

    def test_19_refusal_future_git_commit_logs(self):
        """REFUSAL TEST: Cockpit refuses Day 3 Git repository commit logs."""
        res = self.cockpit.query("Show me git commit logs for the last month")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertIn("I don't know", res["answer"])

    def test_20_refusal_future_pagerduty_incidents(self):
        """REFUSAL TEST: Cockpit refuses Day 3 PagerDuty incident reports."""
        res = self.cockpit.query("What PagerDuty incidents occurred in the second half of October?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertIn("I don't know", res["answer"])


if __name__ == "__main__":
    unittest.main()
