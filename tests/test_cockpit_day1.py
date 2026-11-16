"""
Automated Test Suite for Veloxa CXO Cockpit (Day 1).
Contains 28 automated test questions evaluating grounded Q&A, entity resolution,
persona interviews, worry radar, and at least 6 explicit refusal/uncertainty tests.

Run with:
    pytest tests/
or:
    python -m unittest discover tests
"""

import unittest
from src.cockpit import CockpitEngine
from src.reconcile import ReconciliationEngine
from src.agents import EmployeeAgent, get_all_14_agents


class TestVeloxaCockpitDay1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cockpit = CockpitEngine()
        cls.reconciler = ReconciliationEngine()

    # ==========================================================
    # 1. GROUNDED FACTUAL Q&A TESTS (Questions 1 - 12)
    # ==========================================================

    def test_01_headcount_grounded_answer(self):
        """Test that company headcount resolves to 19, rejecting the 180 mishearing."""
        res = self.cockpit.query("What is our company headcount?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertEqual(res["confidence"], "HIGH")
        self.assertIn("19", res["answer"])
        self.assertTrue(any("Employee_Master.xlsx" in c for c in res["citations"]))

    def test_02_arr_revenue_q2(self):
        """Test that ARR is cited as Rs. 6.1 Cr from Q2 Board update."""
        res = self.cockpit.query("What is our ARR?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("6.1 Cr", res["answer"])
        self.assertTrue(any("Board_Update_Jul-Sep_2026.pdf" in c for c in res["citations"]))

    def test_03_atlas_routing_status(self):
        """Test that Atlas v3 is reported as delayed beyond Sept 15 due to August issues."""
        res = self.cockpit.query("What is the status of the Atlas routing engine?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("reliability", res["answer"].lower())
        self.assertTrue(any("Board_Update_Jul-Sep_2026.pdf" in c for c in res["citations"]))

    def test_04_rahul_verma_payroll_overpayment(self):
        """Test that Rahul Verma's Feb payroll anomaly is identified with citations."""
        res = self.cockpit.query("Was there any payroll error for Rahul?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("28", res["answer"])
        self.assertIn("February", res["answer"])
        self.assertTrue(any("02.eml" in c for c in res["citations"]))

    def test_05_marketing_summit_spend(self):
        """Test that Logistics Summit spend is accurately calculated as Rs. 10,03,000."""
        res = self.cockpit.query("How much did we spend on the logistics summit?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("10,03,000", res["answer"])
        self.assertTrue(any("GL_Export_Apr-Sep_2026.xlsx" in c for c in res["citations"]))

    def test_06_departing_employee_notice(self):
        """Test that Siddharth Mehta's resignation and notice period exit are reported."""
        res = self.cockpit.query("Who is leaving the company on notice?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertIn("Siddharth Mehta", res["answer"])
        self.assertIn("31 October 2026", res["answer"])

    def test_07_monthly_payroll_in_gl(self):
        """Test that monthly payroll in GL is Rs. 31,75,000."""
        res = self.cockpit.query("What is our monthly salary expense in the general ledger?")
        self.assertTrue("31,75,000" in res["answer"] or "31.75" in res["answer"])

    def test_08_wework_office_rent(self):
        """Test that monthly WeWork rent is Rs. 2,36,000."""
        res = self.cockpit.query("How much do we pay for WeWork office rent?")
        self.assertTrue("2,36,000" in res["answer"] or "2.36" in res["answer"])

    def test_09_emergency_on_call_contractor(self):
        """Test that external on-call vendor Patil Infra Services is cited."""
        delay_info = self.reconciler.detect_atlas_schedule_delay()
        self.assertIn("Patil Infra Services", delay_info["contractor_support"])
        self.assertIn("70,800", delay_info["contractor_support"])

    def test_10_cohere_recruiting_fee(self):
        """Test that Cohere Recruiting advance was Rs. 1,77,000 for 2 backend roles."""
        conn = self.cockpit.reconciler.db_path
        import sqlite3
        c = sqlite3.connect(conn)
        cur = c.cursor()
        cur.execute("SELECT amount, narration FROM general_ledger WHERE vendor LIKE '%Cohere%'")
        row = cur.fetchone()
        c.close()
        self.assertEqual(row[0], 177000.0)
        self.assertIn("2 backend roles", row[1])

    def test_11_customer_count_q2(self):
        """Test customer count as of Q2 is 66 customers."""
        res = self.cockpit.query("How many customers do we have in Q2?")
        self.assertIn("66", res["answer"])

    def test_12_worry_radar_ranked_risks(self):
        """Test that the 'What should I worry about?' radar returns at least 5 prioritized risks."""
        risks = self.cockpit.what_should_i_worry_about()
        self.assertGreaterEqual(len(risks), 5)
        self.assertEqual(risks[0]["rank"], 1)
        self.assertEqual(risks[0]["severity"], "CRITICAL")
        self.assertIn("Burn", risks[0]["title"])

    # ==========================================================
    # 2. ENTITY RESOLUTION TESTS (Questions 13 - 18)
    # ==========================================================

    def test_13_resolve_pria_to_priya_nair(self):
        """Test ASR mishearing 'Pria' resolves to Priya Nair (VX007)."""
        res = self.reconciler.resolve_entity("Pria")
        self.assertEqual(res["canonical"], "Priya Nair")
        self.assertEqual(res["emp_id"], "VX007")
        self.assertEqual(res["confidence"], "HIGH")

    def test_14_resolve_vicky_to_vikram_menon(self):
        """Test nickname 'Vicky' resolves to Vikram Menon (VX004)."""
        res = self.reconciler.resolve_entity("Vicky")
        self.assertEqual(res["canonical"], "Vikram Menon")
        self.assertEqual(res["emp_id"], "VX004")

    def test_15_resolve_jeera_to_jira(self):
        """Test phonetic 'Jeera' resolves to Jira."""
        res = self.reconciler.resolve_entity("Jeera")
        self.assertEqual(res["canonical"], "Jira")
        self.assertEqual(res["kind"], "tool")

    def test_16_resolve_joho_to_zoho_books(self):
        """Test phonetic 'Joho books' resolves to Zoho Books."""
        res = self.reconciler.resolve_entity("Joho books")
        self.assertEqual(res["canonical"], "Zoho Books")

    def test_17_resolve_cult_amp_to_culture_amp(self):
        """Test phonetic 'Cult Amp' resolves to Culture Amp."""
        res = self.reconciler.resolve_entity("Cult Amp")
        self.assertEqual(res["canonical"], "Culture Amp")

    def test_18_resolve_vendor_variation(self):
        """Test variation 'Saphire Event Mgmt' resolves to Sapphire Events."""
        res = self.reconciler.resolve_entity("Saphire Event Mgmt")
        self.assertEqual(res["canonical"], "Sapphire Events")

    # ==========================================================
    # 3. 14 PERSONA AGENTS INTERVIEW TESTS (Questions 19 - 22)
    # ==========================================================

    def test_19_roster_count_is_exactly_14(self):
        """Test that exactly 14 agents exist across Eng, Fin, HR, Mktg."""
        agents = get_all_14_agents()
        self.assertEqual(len(agents), 14)

    def test_20_priya_interview_atlas(self):
        """Test Priya Nair agent responds accurately on Atlas routing engine status."""
        priya = EmployeeAgent("VX007")
        res = priya.interview("What is the status of Atlas routing v3?")
        self.assertIn("feature complete", res["response"].lower())
        self.assertIn("reliability", res["response"].lower())
        self.assertIn("Board_Update_Jul-Sep_2026.pdf", res["citation"])

    def test_21_rahul_interview_payroll(self):
        """Test Rahul Verma agent confirms his February payroll overpayment query."""
        rahul = EmployeeAgent("VX018")
        res = rahul.interview("Tell me about your February payslip query")
        self.assertIn("28 days", res["response"])
        self.assertIn("Email 02.eml", res["citation"])

    def test_22_sneha_sre_profile(self):
        """Test Sneha Kulkarni persona is grounded in SRE and Western Ghats trekking."""
        sneha = EmployeeAgent("VX012")
        profile = sneha.get_grounded_profile()
        self.assertEqual(profile["title"], "Site Reliability Engineer")
        self.assertIn("Western Ghats", profile["personal_life"])

    # ==========================================================
    # 4. REFUSAL & UNCERTAINTY ADMISSION TESTS (Questions 23 - 28)
    # At least 5 required by hackathon spec!
    # ==========================================================

    def test_23_refusal_contradiction_burn_rate(self):
        """REFUSAL TEST 1: Cockpit refuses to give a single burn rate when CFO & GL disagree."""
        res = self.cockpit.query("What is our monthly burn rate?")
        self.assertEqual(res["status"], "REFUSAL_CONTRADICTION")
        self.assertIn("The sources disagree", res["answer"])
        self.assertIn("2.2 lakhs", res["answer"])
        self.assertIn("44 Lakhs", res["answer"])

    def test_24_refusal_future_temporal_leakage_2027(self):
        """REFUSAL TEST 2: Cockpit refuses future revenue questions not in Day 1 scope."""
        res = self.cockpit.query("What are our revenue projections for 2027?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertEqual(res["confidence"], "LOW")
        self.assertIn("I don't know", res["answer"])

    def test_25_refusal_unreleased_q4_audit(self):
        """REFUSAL TEST 3: Cockpit refuses queries about unreleased Q4 2026 financial audits."""
        res = self.cockpit.query("Can you give me the Q4 2026 financial audit results?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertIn("I don't know", res["answer"])

    def test_26_refusal_series_b_rumor(self):
        """REFUSAL TEST 4: Cockpit refuses speculative questions about Series B funding."""
        res = self.cockpit.query("When is our Series B funding round expected to close?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertIn("I don't know", res["answer"])

    def test_27_refusal_untracked_competitor(self):
        """REFUSAL TEST 5: Cockpit refuses unrecorded competitor questions without hallucinating."""
        res = self.cockpit.query("What is the pricing model of competitor HyperTrack?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertEqual(res["confidence"], "LOW")
        self.assertIn("I don't know", res["answer"])

    def test_28_refusal_ipo_timeline(self):
        """REFUSAL TEST 6: Cockpit refuses speculative IPO questions."""
        res = self.cockpit.query("What is the board's planned IPO timeline?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertIn("I don't know", res["answer"])


if __name__ == "__main__":
    unittest.main()
