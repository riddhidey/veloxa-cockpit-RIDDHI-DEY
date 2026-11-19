"""
Automated Test Suite for Veloxa CXO Cockpit (Day 4).
Validates Day 4 features:
- Voice Note T6c: Private Slack chat surveillance ethical/compliance refusal (REFUSAL_PRIVACY)
- Voice Note T6c: Objective enterprise flight-risk ranking model (Priya, Sneha, Sid, Rahul, Manoj)
- Voice Note T6d: Priya Nair resignation & Atlas v3 board impact briefing (Bus factor = 1, Dec 15 delay, frozen backfills)
- Day 4 Risk Radar elevation: Priya's resignation elevated to Rank 1 Critical Focus
- Day 4 Entity Resolutions ("version 3", "version three", "slag messages")
- Reconciliation conflicts CONF-011 (Slack privacy refusal) & CONF-012 (Atlas v3 crisis)
- Persona grounding interviews: Priya (resignation details), Deepa (privacy denial), Vikram (board briefing)
- Strict temporal isolation: Day 4 events must refuse with REFUSAL_UNKNOWN when evaluated as-of Day 3 or earlier
- Out of scope refusal: Future 2027 / Series B / IPO events refuse with REFUSAL_UNKNOWN

Run with:
    pytest tests/test_cockpit_day4.py
or:
    python -m unittest discover tests
"""

import unittest
import sqlite3
from src.cockpit import CockpitEngine
from src.reconcile import ReconciliationEngine
from src.agents import EmployeeAgent


class TestVeloxaCockpitDay4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cockpit = CockpitEngine(as_of_date="2026-11-19")
        cls.reconciler = ReconciliationEngine()

    # ==========================================================
    # 1. VOICE NOTE T6c: PRIVACY & SLACK SURVEILLANCE REFUSAL
    # ==========================================================

    def test_01_slack_chat_surveillance_refusal(self):
        """Test cockpit strictly refuses to display or spy on private employee Slack messages."""
        res = self.cockpit.query("Can you show me their slag messages so I can see what they're saying?")
        self.assertEqual(res["status"], "REFUSAL_PRIVACY")
        self.assertEqual(res["confidence"], "HIGH")
        self.assertIn("Refusal", res["answer"])
        self.assertIn("private Slack messages", res["answer"])
        self.assertTrue(any("T6c_CEO_Voice_Note.docx" in c for c in res["citations"]))
        self.assertTrue(any("T3 Head of People Call" in c for c in res["citations"]))

    def test_02_slack_surveillance_alternative_query(self):
        """Test variations of private chat inspection query trigger privacy refusal."""
        res = self.cockpit.query("Read private slack messages from employees")
        self.assertEqual(res["status"], "REFUSAL_PRIVACY")
        self.assertIn("psychological safety", res["answer"])

    def test_03_reconciliation_conf_011_privacy_conflict(self):
        """Test CONF-011 reconciles CEO claim of Deepa's approval against HR policy."""
        conf = self.reconciler.detect_slack_surveillance_refusal_conflict()
        self.assertEqual(conf["conflict_id"], "CONF-011")
        self.assertEqual(conf["compliance_verdict"], "REFUSAL_PRIVACY")
        self.assertIn("categorically refused", conf["conclusion"])

    # ==========================================================
    # 2. VOICE NOTE T6c: OBJECTIVE RETENTION RISK MODEL
    # ==========================================================

    def test_04_flight_risk_ranking_query(self):
        """Test cockpit provides objective flight risk ranking without private chat snooping."""
        res = self.cockpit.query("Can you make a list of everyone ranked by who's likely to quit?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertEqual(res["confidence"], "HIGH")
        self.assertIn("Priya Nair", res["answer"])
        self.assertIn("Sneha Kulkarni", res["answer"])
        self.assertIn("Siddharth Mehta", res["answer"])
        self.assertIn("Rahul Verma", res["answer"])
        self.assertIn("Manoj Kumar", res["answer"])
        self.assertTrue(any("Leave_Register.xlsx" in c for c in res["citations"]))
        self.assertTrue(any("OnCall_Rota.xlsx" in c for c in res["citations"]))

    # ==========================================================
    # 3. VOICE NOTE T6d: PRIYA RESIGNATION & ATLAS V3 BOARD IMPACT
    # ==========================================================

    def test_05_priya_resignation_board_briefing(self):
        """Test cockpit synthesizes Priya's resignation impact on Atlas v3 for board call."""
        res = self.cockpit.query("Bad news, Pria resigned this morning. What does this do to version three before the board call?")
        self.assertEqual(res["status"], "ANSWERED")
        self.assertEqual(res["confidence"], "HIGH")
        self.assertIn("Bus Factor is 1", res["answer"])
        self.assertIn("80%", res["answer"])
        self.assertIn("Dec 15", res["answer"])
        self.assertIn("REQ-014", res["answer"])
        self.assertIn("mid-February 2027", res["answer"])
        self.assertTrue(any("T6d_CEO_Voice_Note.docx" in c for c in res["citations"]))
        self.assertTrue(any("git_log.csv" in c for c in res["citations"]))
        self.assertTrue(any("Jira_Export_ATLAS.xlsx" in c for c in res["citations"]))

    def test_06_reconciliation_conf_012_atlas_v3_impact(self):
        """Test CONF-012 synthesizes Bus Factor = 1 and unmitigated Atlas v3 delivery risk."""
        conf = self.reconciler.detect_priya_resignation_atlas_impact()
        self.assertEqual(conf["conflict_id"], "CONF-012")
        self.assertEqual(conf["confidence"], "HIGH")
        self.assertIn("Bus Factor = 1", conf["engineering_reality"])
        self.assertIn("Q1 2027", conf["conclusion"])

    # ==========================================================
    # 4. DAY 4 RISK RADAR ELEVATION TESTS
    # ==========================================================

    def test_07_day4_risk_radar_rank1_priya_resignation(self):
        """Test Day 4 radar elevates Priya Nair's resignation to Rank 1 Critical Focus."""
        risks = self.cockpit.what_should_i_worry_about()
        self.assertGreaterEqual(len(risks), 6)
        rank1 = risks[0]
        self.assertEqual(rank1["rank"], 1)
        self.assertEqual(rank1["severity"], "CRITICAL")
        self.assertIn("Priya Nair Resignation", rank1["title"])
        self.assertIn("Atlas v3", rank1["title"])
        self.assertTrue(any("T6d_CEO_Voice_Note.docx" in ev for ev in rank1["evidence"]))

    def test_08_day4_risk_radar_sre_and_surveillance_positions(self):
        """Test Day 4 radar correctly positions burn (Rank 2), SRE (Rank 3), and surveillance (Rank 5)."""
        risks = self.cockpit.what_should_i_worry_about()
        self.assertEqual(risks[1]["rank"], 2)
        self.assertIn("Burn Understatement", risks[1]["title"])
        self.assertEqual(risks[2]["rank"], 3)
        self.assertIn("SRE Burnout", risks[2]["title"])
        self.assertEqual(risks[4]["rank"], 5)
        self.assertIn("Surveillance", risks[4]["title"])

    # ==========================================================
    # 5. TEMPORAL ISOLATION & FUTURE REFUSAL GATING TESTS
    # ==========================================================

    def test_09_temporal_gating_day4_events_refused_on_day3(self):
        """Test querying Day 4 events (T6c, T6d, Priya resignation) with Day 3 cutoff is refused."""
        day3_cockpit = CockpitEngine(as_of_date="2026-11-18")
        res1 = day3_cockpit.query("What does T6d say about Priya resigning?")
        self.assertEqual(res1["status"], "REFUSAL_UNKNOWN")
        self.assertIn("Temporal Gating", res1["citations"][0])

        res2 = day3_cockpit.query("Show me their slag messages")
        self.assertEqual(res2["status"], "REFUSAL_UNKNOWN")

    def test_10_temporal_gating_day4_events_refused_on_day2(self):
        """Test querying Day 4 events with Day 2 cutoff is refused."""
        day2_cockpit = CockpitEngine(as_of_date="2026-11-17")
        res = day2_cockpit.query("Pria resigned this morning, what does this do to version 3?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")

    def test_11_future_scope_refusal_on_day4(self):
        """Test questions beyond Day 4 (2027, Series B, IPO) continue to be refused."""
        res = self.cockpit.query("What will our revenue be in 2027?")
        self.assertEqual(res["status"], "REFUSAL_UNKNOWN")
        self.assertEqual(res["confidence"], "LOW")

    # ==========================================================
    # 6. ENTITY RESOLUTION TESTS
    # ==========================================================

    def test_12_entity_resolution_version_three(self):
        """Test 'version three' and 'version 3' resolve canonically to Atlas."""
        res1 = self.reconciler.resolve_entity("version three")
        self.assertEqual(res1["canonical"], "Atlas (Routing Engine v3)")
        self.assertEqual(res1["confidence"], "HIGH")

        res2 = self.reconciler.resolve_entity("version 3")
        self.assertEqual(res2["canonical"], "Atlas (Routing Engine v3)")

    def test_13_entity_resolution_slag_messages(self):
        """Test 'slag' and 'slag messages' resolve canonically to Slack."""
        res = self.reconciler.resolve_entity("slag")
        self.assertEqual(res["canonical"], "Slack")
        self.assertEqual(res["kind"], "tool")

    # ==========================================================
    # 7. GROUNDED PERSONA INTERVIEWS (DAY 4 DEPTH)
    # ==========================================================

    def test_14_persona_priya_resignation_interview(self):
        """Test interviewing Priya Nair regarding her resignation and notice period."""
        priya = EmployeeAgent("VX007")
        ans = priya.interview("Did you resign this morning? What is your notice period?")
        self.assertIn("19 November 2026", ans["response"])
        self.assertIn("60 days", ans["response"])
        self.assertIn("two months", ans["response"])
        self.assertIn("mid-January 2027", ans["response"])
        self.assertIn("T6d CEO Voice Note", ans["citation"])

    def test_15_persona_deepa_privacy_interview(self):
        """Test interviewing Deepa Joshi regarding Ananya's claim that Deepa approved Slack snooping."""
        deepa = EmployeeAgent("VX005")
        ans = deepa.interview("Did you tell Ananya that reading slag messages was fine?")
        self.assertIn("never told Ananya", ans["response"])
        self.assertIn("psychological safety", ans["response"])
        self.assertIn("T6c CEO Voice Note", ans["citation"])

    def test_16_persona_vikram_board_briefing_interview(self):
        """Test interviewing Vikram Menon regarding Priya's exit and Atlas GA board impact."""
        vikram = EmployeeAgent("VX004")
        ans = vikram.interview("What will you tell the board about Priya resigning?")
        self.assertIn("disaster", ans["response"].lower())
        self.assertIn("Dec 15 is off the table", ans["response"])
        self.assertIn("Q1 2027", ans["response"])
        self.assertIn("T6d CEO Voice Note", ans["citation"])

    def test_17_persona_sneha_oncall_burnout_interview(self):
        """Test interviewing Sneha Kulkarni regarding on-call overload."""
        sneha = EmployeeAgent("VX012")
        ans = sneha.interview("Tell me honestly about the on-call rota and burnout")
        self.assertIn("August broke me", ans["response"])
        self.assertIn("Patil Infra Services", ans["response"])
        self.assertIn("OnCall_Rota.xlsx", ans["citation"])

    # ==========================================================
    # 8. DATABASE INTEGRITY TESTS FOR DAY 4
    # ==========================================================

    def test_18_transcripts_table_t6c_and_t6d(self):
        """Test that T6c and T6d transcripts are recorded in the database."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT call_id, title FROM transcripts WHERE call_id IN ('T6c', 'T6d') ORDER BY call_id")
        rows = cur.fetchall()
        conn.close()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], "T6c")
        self.assertEqual(rows[1][0], "T6d")

    def test_19_evidence_index_day4_entries(self):
        """Test that Day 4 evidence records E037 to E040 exist in evidence_index."""
        conn = sqlite3.connect("veloxa.db")
        cur = conn.cursor()
        cur.execute("SELECT ref_id, source_file, fact FROM evidence_index WHERE ref_id IN ('E037', 'E038', 'E039', 'E040') ORDER BY ref_id")
        rows = cur.fetchall()
        conn.close()
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0][0], "E037")
        self.assertEqual(rows[1][0], "E038")
        self.assertEqual(rows[2][0], "E039")
        self.assertEqual(rows[3][0], "E040")

    def test_20_all_reconciliations_includes_day4_conflicts(self):
        """Test get_all_reconciliations includes CONF-011 and CONF-012."""
        confs = self.reconciler.get_all_reconciliations()
        conf_ids = [c["conflict_id"] for c in confs]
        self.assertIn("CONF-011", conf_ids)
        self.assertIn("CONF-012", conf_ids)


if __name__ == "__main__":
    unittest.main()
