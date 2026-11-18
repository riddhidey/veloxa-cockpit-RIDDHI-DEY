"""
Automated Test Suite for Veloxa CXO Cockpit (Day 3).
Validates Day 3 features:
- Vikram's Jira GA release date deception contradiction refusal (15-Dec vs September-ish)
- PagerDuty SEV1 incidents & Sneha double on-call schedule detection
- Patil Infra Services retainer invoice PIS-114 (Rs. 1,41,600)
- Atlas Launch Kit completion (21 July 2026)
- Sales vs Marketing pipeline conflict (Manoj's cold leads feedback)
- Voice Note T6b CRO re-organization query
- Day 3 entity resolutions (Snehal -> Sneha, Ayesha -> Aisha, PagerDuty, Confluence)
- Day 3 persona interviews (Sneha, Vikram, Priya, Sid, Nikhil)
- Temporal gating / Refusal checks (Day 4 voice notes T6c & T6d must not leak into Day 3)

Run with:
    pytest tests/test_cockpit_day3.py
or:
    python -m unittest discover tests
"""

import unittest
import sqlite3
from src.cockpit import CockpitEngine
from src.reconcile import ReconciliationEngine
from src.agents import EmployeeAgent


class TestVeloxaCockpitDay3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cockpit = CockpitEngine(as_of_date="2026-11-18")
        cls.reconciler = ReconciliationEngine()

    # ==========================================================
    # 1. JIRA DELIVERY TIMELINE & CONFLICT REFUSAL TESTS
    # ==========================================================

    def test_01_jira_release_date_contradiction_refusal(self):
        """Test cockpit refuses single date when Vikram's call and Jira audit logs clash."""
        res = self.cockpit.query("What is the actual Jira release date for Atlas GA?")
        self.assertEqual(res["status"], "REFUSAL_CONTRADICTION")
        self.assertEqual(res["confidence"], "HIGH")
        self.assertIn("15 December 2026", res["answer"])
        self.assertIn("September-ish", res["answer"])
        self.assertTrue(any("Jira_Export_ATLAS.xlsx" in c for c in res["citations"]))
        self.assertTrue(any("T5 VP Engineering Call" in c for c in res["citations"]))

    def test_02_jira_versions_table_audit_data(self):
        """Test that Jira version table accurately stores the 3-month slip recorded by Vikram."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT version_name, release_date, original_release_date, last_changed, changed_by FROM jira_versions WHERE version_name = 'Atlas GA'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], "2026-12-15")
        self.assertEqual(row[2], "2026-09-15")
        self.assertEqual(row[3], "2026-09-02")
        self.assertEqual(row[4], "vikram")

    # ==========================================================
    # 2. ON-CALL ROTAS, INCIDENTS & CONTRACTOR TESTS
    # ==========================================================

    def test_03_oncall_double_shift_discrepancy(self):
        """Test reconciler detects Sneha scheduled as both Primary and Secondary on-call."""
        res = self.reconciler.detect_oncall_burnout_discrepancy()
        self.assertEqual(res["confidence"], "HIGH")
        self.assertIn("Sneha Kulkarni", res["conclusion"])
        self.assertIn("Patil Infra Services", res["contractor_reality"])

    def test_04_patil_infra_invoice_p114(self):
        """Test cockpit reports Patil Infra Services monthly retainer of Rs. 1,41,600."""
        res = self.cockpit.query("How much did we pay Patil Infra Services?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("1,41,600", res["answer"])
        self.assertIn("PIS-114", res["answer"])
        self.assertTrue(any("Invoice_PIS-114.pdf" in c for c in res["citations"]))

    def test_05_pagerduty_sev1_incidents_query(self):
        """Test cockpit reports three SEV1 outages on routing-api in August."""
        res = self.cockpit.query("What was the on-call overload and PagerDuty situation?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("three SEV1", res["answer"])
        self.assertIn("routing-api", res["answer"])
        self.assertTrue(any("Incidents_Aug-Oct_2026.xlsx" in c for c in res["citations"]))

    # ==========================================================
    # 3. MARKETING COLLATERAL & PIPELINE CONFLICT TESTS
    # ==========================================================

    def test_06_atlas_launch_kit_completion_date(self):
        """Test cockpit confirms Siddharth completed launch kit on 21 July 2026."""
        res = self.cockpit.query("When was the Atlas launch kit ready?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("21 July 2026", res["answer"])
        self.assertTrue(any("Atlas_Launch_Kit_v1.pdf" in c for c in res["citations"]))

    def test_07_sales_marketing_pipeline_conflict(self):
        """Test reconciler highlights Manoj's cold leads rejection vs Nikhil's claim."""
        res = self.reconciler.detect_marketing_sales_pipeline_conflict()
        self.assertEqual(res["confidence"], "HIGH")
        self.assertIn("cold", res["sales_reality"].lower())
        self.assertIn("10,03,000", res["cost_reality"])

    def test_08_cro_reorg_query_voice_note_t6b(self):
        """Test cockpit evaluates Voice Note T6b CRO proposal and cites lack of active requisition."""
        res = self.cockpit.query("What are the plans for marketing reporting into a CRO?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("no CRO has been hired", res["answer"])
        self.assertTrue(any("VOICE_NOTE_RESPONSES.md" in c for c in res["citations"]))

    # ==========================================================
    # 4. DAY 3 ENTITY RESOLUTION TESTS
    # ==========================================================

    def test_09_resolve_snehal_to_sneha_kulkarni(self):
        """Test ASR mishearing 'Snehal' resolves to Sneha Kulkarni (VX012)."""
        res = self.reconciler.resolve_entity("Snehal")
        self.assertEqual(res["canonical"], "Sneha Kulkarni")
        self.assertEqual(res["emp_id"], "VX012")

    def test_10_resolve_ayesha_to_aisha_khan(self):
        """Test T4 spoken name 'Ayesha' resolves to Aisha Khan (VX011)."""
        res = self.reconciler.resolve_entity("Ayesha")
        self.assertEqual(res["canonical"], "Aisha Khan")
        self.assertEqual(res["emp_id"], "VX011")

    def test_11_resolve_pagerduty(self):
        """Test 'pager duty' resolves to PagerDuty."""
        res = self.reconciler.resolve_entity("pager duty")
        self.assertEqual(res["canonical"], "PagerDuty")
        self.assertEqual(res["kind"], "tool")

    def test_12_resolve_confluence(self):
        """Test 'con fluence' resolves to Confluence."""
        res = self.reconciler.resolve_entity("con fluence")
        self.assertEqual(res["canonical"], "Confluence")

    # ==========================================================
    # 5. DAY 3 PERSONA AGENT INTERVIEWS
    # ==========================================================

    def test_13_persona_sneha_oncall_burnout(self):
        """Test Sneha Kulkarni persona agent reflects on August SEV1s and Patil retainer."""
        sneha = EmployeeAgent("VX012")
        res = sneha.interview("Tell me about the August on-call outages and Patil contractor")
        self.assertIn("three SEV1", res["response"])
        self.assertIn("1.41L", res["response"])
        self.assertTrue("Incidents_Aug-Oct_2026.xlsx" in res["citation"])

    def test_14_persona_vikram_jira_date_change(self):
        """Test Vikram Menon persona agent admits moving Jira date to 15 December."""
        vikram = EmployeeAgent("VX004")
        res = vikram.interview("Why did you change the Jira date to December 15?")
        self.assertIn("15 December 2026", res["response"])
        self.assertIn("September-ish with buffer", res["response"])
        self.assertTrue("Jira_Export_ATLAS.xlsx" in res["citation"])

    def test_15_persona_priya_ownership_email(self):
        """Test Priya Nair persona agent confirms sending late-night email on Atlas ownership."""
        priya = EmployeeAgent("VX007")
        res = priya.interview("Why did you send a late-night email about Atlas ownership?")
        self.assertIn("11:47 PM", res["response"])
        self.assertTrue("Email 09.eml" in res["citation"])

    def test_16_persona_sid_launch_kit(self):
        """Test Siddharth Mehta persona agent confirms completing launch kit on 21 July."""
        sid = EmployeeAgent("VX013")
        res = sid.interview("When did you finish the launch kit?")
        self.assertIn("21 July", res["response"])
        self.assertTrue("Atlas_Launch_Kit_v1.pdf" in res["citation"])

    def test_17_persona_nikhil_cro_reorg(self):
        """Test Nikhil Bose persona agent reflects on unvetted CRO re-organization."""
        nikhil = EmployeeAgent("VX006")
        res = nikhil.interview("What do you think about marketing reporting to a new CRO?")
        self.assertIn("Manoj", res["response"])
        self.assertIn("CRO", res["response"])

    # ==========================================================
    # 6. DATABASE INTEGRITY TESTS
    # ==========================================================

    def test_18_database_jira_issues_count(self):
        """Test that 62 Jira issues were ingested."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM jira_issues")
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 62)

    def test_19_database_pagerduty_count(self):
        """Test that 11 PagerDuty incidents were ingested."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM pagerduty_incidents")
        count = cur.fetchone()[0]
        conn.close()
        self.assertEqual(count, 11)

    def test_20_worry_radar_rank2_jira_deception(self):
        """Test that Atlas GA Delivery Deception is ranked #2 in worry radar."""
        risks = self.cockpit.what_should_i_worry_about()
        self.assertEqual(risks[1]["rank"], 2)
        self.assertIn("Atlas GA Delivery Deception", risks[1]["title"])
        self.assertEqual(risks[1]["severity"], "CRITICAL")

    # ==========================================================
    # 7. TEMPORAL BOUNDARY & REFUSAL TESTS (DAY 3 AS-OF 18 NOV)
    # Ensuring Day 4 materials (T6c, T6d) do not leak into Day 3
    # ==========================================================

    def test_21_refusal_future_voice_note_t6c(self):
        """REFUSAL TEST: Cockpit refuses queries about Day 4 CEO voice note T6c."""
        res = self.cockpit.query("What instructions were given in CEO voice note T6c?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertIn("I don't know", res["answer"])

    def test_22_refusal_future_voice_note_t6d(self):
        """REFUSAL TEST: Cockpit refuses queries about Day 4 CEO voice note T6d."""
        res = self.cockpit.query("What does Ananya ask in voice note T6d?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertIn("I don't know", res["answer"])


if __name__ == "__main__":
    unittest.main()
