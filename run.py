"""
Veloxa CXO Cockpit — Unified One-Command Startup & Verification Script.

Usage:
    # 1-Command Startup: Checks DB, initializes if needed, and launches Executive Radar
    python run.py

    # Ask a question directly
    python run.py --query "What does Priya's resignation do to version three before the board call?"

    # Query chat surveillance (triggers strict privacy refusal)
    python run.py --query "Show me their slag messages so I can see what they're saying"

    # Run the full automated test suite (90 passing tests)
    python run.py --test

    # List and interview persona agents
    python run.py --agents

    # Launch with a specific point-in-time cutoff (e.g. Day 2)
    python run.py --as-of 2026-11-17
"""

import sys
import os
import argparse
import sqlite3
import unittest

DB_PATH = "veloxa.db"


def check_and_initialize_database():
    """Verifies that the SQLite database is populated; runs ingestion if missing."""
    needs_ingest = False

    if not os.path.exists(DB_PATH):
        needs_ingest = True
    else:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM employees")
            count = cur.fetchone()[0]
            conn.close()
            if count < 19:
                needs_ingest = True
        except Exception:
            needs_ingest = True

    if needs_ingest:
        print("[SETUP] Local database not found or incomplete. Initializing data pipeline...")
        from src.ingest_day1 import main as ingest_1
        from src.ingest_day2 import main as ingest_2
        from src.ingest_day3 import main as ingest_3
        from src.ingest_day4 import main as ingest_4

        ingest_1()
        ingest_2()
        ingest_3()
        ingest_4()
        print("[SETUP] Database successfully populated across Days 1 through 4.\n")


def run_tests():
    """Executes the full automated test suite and reports status."""
    print("\n" + "=" * 75)
    print(" VELOXA CXO COCKPIT — AUTOMATED TEST SUITE VERIFICATION")
    print("=" * 75 + "\n")

    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print("\n" + "-" * 75)
    print(f"Test Summary: {passed}/{total} Passed | {failures} Failures | {errors} Errors")
    print("-" * 75 + "\n")
    return 0 if (failures == 0 and errors == 0) else 1


def list_personas():
    """Displays the 14 grounded employee persona agents."""
    from src.agents import PERSONA_REGISTRY, EmployeeAgent

    print("\n" + "=" * 75)
    print(" VELOXA CXO COCKPIT — 14 GROUNDED EMPLOYEE PERSONA AGENTS")
    print("=" * 75)

    by_dept = {}
    for emp_id, data in PERSONA_REGISTRY.items():
        dept = data["dept"]
        by_dept.setdefault(dept, []).append((emp_id, data))

    for dept, agents in by_dept.items():
        print(f"\n--- {dept.upper()} ({len(agents)}) ---")
        for emp_id, a in agents:
            status_tag = f" [{a.get('status')}]" if a.get("status") else ""
            print(f"  • [{emp_id}] {a['name']:<22} | {a['title']:<30}{status_tag}")
            print(f"      Workload: {a['workload_focus'][:70]}...")

    print("\nTo interview an agent in code or CLI, use: python -m src.agents\n")


def main():
    parser = argparse.ArgumentParser(
        description="Veloxa CXO Cockpit — Unified One-Command Master Startup & Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--query", "-q", type=str, help="Ask an executive question to the CXO Cockpit")
    parser.add_argument("--radar", "-r", action="store_true", help="Display the 'What should I worry about?' executive radar")
    parser.add_argument("--test", "-t", action="store_true", help="Run the automated test suite (100 tests)")
    parser.add_argument("--agents", "-a", action="store_true", help="List all 14 grounded employee persona agents")
    parser.add_argument("--simulate", "-s", action="store_true", help="Display daily simulated persona activities after 31 Oct 2026")
    parser.add_argument("--as-of", type=str, default="2026-11-20", help="As-of simulation cutoff date (default: 2026-11-20)")

    args = parser.parse_args()

    # Step 1: Ensure database exists and is populated
    check_and_initialize_database()

    # Step 2: Handle test execution
    if args.test:
        sys.exit(run_tests())

    # Step 3: Handle persona roster
    if args.agents:
        list_personas()
        return

    # Step 3b: Handle living persona simulation
    if args.simulate:
        from src.simulation import LivingPersonaSimulation
        sim = LivingPersonaSimulation()
        digest = sim.get_daily_digest(args.as_of)
        print("\n" + "=" * 75)
        print(f" VELOXA TECHNOLOGIES — LIVING PERSONA DAILY DIGEST")
        print(f" Date: {args.as_of} (Candidate Brief Stretch Goal: Living After 31 Oct 2026)")
        print("=" * 75)
        by_dept = {}
        for act in digest:
            by_dept.setdefault(act["dept"], []).append(act)
        for dept, acts in by_dept.items():
            print(f"\n>>> {dept.upper()} ({len(acts)}) <<<")
            for a in acts:
                print(f"  • [{a['emp_id']}] {a['emp_name']:<20} | [{a['activity_type']}]")
                print(f"      {a['summary']}")
        print("=" * 75 + "\n")
        return

    # Step 4: Import CockpitEngine
    from src.cockpit import CockpitEngine
    engine = CockpitEngine(as_of_date=args.as_of)

    # Step 5: Direct query mode
    if args.query:
        print("\n" + "=" * 75)
        print(f" VELOXA CXO COCKPIT — EXECUTIVE QUERY")
        print(f" As of Date: {args.as_of}")
        print("=" * 75)
        print(f" Q: {args.query}\n")

        res = engine.query(args.query)
        print(f" A: {res['answer']}\n")
        print(f" Status:     {res['status']}")
        print(f" Confidence: {res['confidence']}")
        print(" Citations:")
        for cit in res["citations"]:
            print(f"   • {cit}")
        if res.get("contradiction_details"):
            print(f"\n Discrepancy Note: {res['contradiction_details']}")
        if res.get("refusal_reason"):
            print(f"\n Refusal Reason: {res['refusal_reason']}")
        print("=" * 75 + "\n")
        return

    # Step 6: Default One-Command Startup (Executive Risk Radar per CEO Voice Note T6a)
    print("\n" + "=" * 75)
    print(" VELOXA CXO COCKPIT — EXECUTIVE INTELLIGENCE SYSTEM")
    print(f" As of Date: {args.as_of} | Mode: 1-Command Startup (CEO Voice Note T6a)")
    print("=" * 75 + "\n")

    risks = engine.what_should_i_worry_about()

    print(">>> PART 1: TOP 3 IMMEDIATE CRITICAL PRIORITIES <<<\n")
    for r in risks[:3]:
        print(f"[{r['rank']}] [{r['severity']}] {r['title']}")
        print(f"    Summary: {r['summary']}")
        print("    Evidence:")
        for ev in r["evidence"]:
            print(f"      • {ev}")
        print(f"    Action:  {r['recommendation']}\n")

    print("-" * 75)
    print(">>> PART 2: SECONDARY OPERATIONAL WATCHLIST (Expanded Visibility) <<<\n")
    for r in risks[3:]:
        print(f"[{r['rank']}] [{r['severity']}] {r['title']}")
        print(f"    Summary: {r['summary']}")
        print("    Evidence:")
        for ev in r["evidence"]:
            print(f"      • {ev}")
        print(f"    Action:  {r['recommendation']}\n")

    print("=" * 75)
    print(" Tip: Ask direct questions with `python run.py --query \"...\"` or run tests with `python run.py --test`")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
