"""
Automated Test Suite for Veloxa Living Persona Simulation (Stretch Goal).
Validates that employee personas continue living after 31 October 2026:
- Daily activities generated for all 14 personas across Eng, Finance, People, Marketing
- Priya Nair's 19-Nov resignation event and 60-day notice handover tracking
- Siddharth Mehta's post-31 Oct departed alumni status
- Sneha Kulkarni's on-call relief sync with Patil Infra Services
- Deepa Joshi's retention 1:1s and chat surveillance pushback
- Database persistence in daily_agent_activities table

Run with:
    pytest tests/test_simulation.py
or:
    python -m unittest discover tests
"""

import unittest
import sqlite3
from src.simulation import LivingPersonaSimulation


class TestLivingPersonaSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = LivingPersonaSimulation()
        cls.sim.simulate_range("2026-11-01", "2026-11-20")

    def test_01_simulation_table_exists(self):
        """Test daily_agent_activities table exists and is populated."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM daily_agent_activities")
        count = cur.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(count, 14 * 20)

    def test_02_simulate_day_covers_all_14_personas(self):
        """Test that every day simulates all 14 personas."""
        digest = self.sim.get_daily_digest("2026-11-18")
        self.assertEqual(len(digest), 14)
        emp_ids = {a["emp_id"] for a in digest}
        self.assertIn("VX007", emp_ids)  # Priya
        self.assertIn("VX012", emp_ids)  # Sneha
        self.assertIn("VX004", emp_ids)  # Vikram
        self.assertIn("VX013", emp_ids)  # Siddharth

    def test_03_priya_resignation_activity_on_nov_19(self):
        """Test Priya Nair's activity on 19 Nov reflects her formal resignation."""
        timeline = self.sim.get_agent_timeline("VX007", limit=30)
        nov19_acts = [a for a in timeline if a["sim_date"] == "2026-11-19"]
        self.assertTrue(len(nov19_acts) > 0)
        priya_nov19 = nov19_acts[0]
        self.assertEqual(priya_nov19["activity_type"], "RESIGNATION_NOTICE")
        self.assertIn("60-day notice", priya_nov19["summary"])

    def test_04_priya_notice_period_handover_after_nov_19(self):
        """Test Priya's post-resignation days focus on architecture handover and remaining days."""
        timeline = self.sim.get_agent_timeline("VX007", limit=30)
        nov20_acts = [a for a in timeline if a["sim_date"] == "2026-11-20"]
        self.assertTrue(len(nov20_acts) > 0)
        priya_nov20 = nov20_acts[0]
        self.assertEqual(priya_nov20["activity_type"], "ARCHITECTURE_HANDOVER")
        self.assertIn("days remaining", priya_nov20["summary"])

    def test_05_siddharth_post_oct31_alumni_status(self):
        """Test Siddharth Mehta is recorded as departed alumni after 31 October 2026."""
        timeline = self.sim.get_agent_timeline("VX013", limit=10)
        for act in timeline:
            if act["sim_date"] > "2026-10-31":
                self.assertEqual(act["activity_type"], "ALUMNI_STATUS")
                self.assertIn("Departed employee", act["summary"])

    def test_06_sneha_oncall_relief_with_patil_infra(self):
        """Test Sneha Kulkarni's simulation reflects on-call relief and database tuning."""
        timeline = self.sim.get_agent_timeline("VX012", limit=10)
        types = {a["activity_type"] for a in timeline}
        self.assertTrue("INFRA_HANDOVER" in types or "SRE_MAINTENANCE" in types)

    def test_07_deepa_retention_and_privacy_pushback(self):
        """Test Deepa's activity includes retention intervention and chat privacy pushback."""
        timeline = self.sim.get_agent_timeline("VX005", limit=10)
        nov19_act = [a for a in timeline if a["sim_date"] == "2026-11-19"][0]
        self.assertEqual(nov19_act["activity_type"], "RETENTION_INTERVENTION")
        self.assertIn("chat surveillance", nov19_act["summary"])

    def test_08_vikram_q1_2027_rebaselining(self):
        """Test Vikram's activity following Priya's resignation plans for Q1 2027 GA."""
        timeline = self.sim.get_agent_timeline("VX004", limit=10)
        nov19_act = [a for a in timeline if a["sim_date"] == "2026-11-19"][0]
        self.assertEqual(nov19_act["activity_type"], "EXECUTIVE_CONTINGENCY")
        self.assertIn("Q1 2027", nov19_act["summary"])

    def test_09_meera_burn_rate_tracking(self):
        """Test Meera Iyer tracks burn rate against Rs. 6.18 Cr cash balance."""
        timeline = self.sim.get_agent_timeline("VX003", limit=10)
        act = timeline[0]
        self.assertEqual(act["activity_type"], "FINANCIAL_MODELING")
        self.assertIn("6.18 Cr", act["summary"])

    def test_10_daily_digest_covers_all_four_departments(self):
        """Test daily digest categorizes across all four required departments."""
        digest = self.sim.get_daily_digest("2026-11-20")
        depts = {a["dept"] for a in digest}
        self.assertIn("Engineering", depts)
        self.assertIn("Finance", depts)
        self.assertIn("People & Ops", depts)
        self.assertIn("Marketing", depts)


if __name__ == "__main__":
    unittest.main()
