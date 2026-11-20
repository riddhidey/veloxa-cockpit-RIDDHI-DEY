"""
Veloxa CXO Cockpit — Living Persona Simulation Engine.
Implements Candidate Brief Stretch Goal:
'Agents that keep living after 31 Oct 2026 and generate new activity day by day.'

Simulates daily activities, standups, commits, and operational events for all 14
grounded personas across Engineering, Finance, People & Ops, and Marketing.
"""

import os
import sqlite3
import datetime
from typing import Dict, List, Optional, Any
from src.agents import PERSONA_REGISTRY

DB_PATH = "veloxa.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_simulation_tables():
    """Create the daily_agent_activities table in veloxa.db."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_agent_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sim_date TEXT NOT NULL,
            emp_id TEXT NOT NULL,
            emp_name TEXT NOT NULL,
            dept TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            details TEXT,
            metadata TEXT,
            UNIQUE(sim_date, emp_id)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_activity_date ON daily_agent_activities(sim_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_activity_emp ON daily_agent_activities(emp_id)")
    conn.commit()
    conn.close()


class LivingPersonaSimulation:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_simulation_tables()

    def generate_persona_activity(self, emp_id: str, date_str: str) -> Dict[str, Any]:
        """
        Generates grounded, day-by-day simulated activity for an employee persona
        after 31 October 2026, reflecting active company events:
        - Siddharth Mehta's post-Oct 31 exit status
        - Priya Nair's 60-day notice period and handoff documentation
        - Sneha Kulkarni's on-call relief via contractor Patil Infra
        - Meera's cash burn tracking against Rs. 6.18 Cr
        - Deepa's retention 1:1s and privacy policy work
        - Vikram's Q1 2027 roadmap re-baselining
        """
        persona = PERSONA_REGISTRY.get(emp_id)
        if not persona:
            return {}

        name = persona["name"]
        dept = persona["dept"]
        title = persona["title"]

        # Date parsing
        try:
            curr_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            curr_date = datetime.date(2026, 11, 19)

        # Days into November 2026
        day_num = curr_date.day

        # === 1. PRIYA NAIR (VX007) ===
        if emp_id == "VX007":
            if curr_date < datetime.date(2026, 11, 19):
                act_type = "ENGINEERING_SPRINT"
                summary = "Benchmarking routing engine latency under simulated high-load spikes"
                details = (
                    "Investigating lock contention in PostgreSQL routing table. Mentored Rahul Verma on "
                    "Kafka telemetry consumer offsets. Sent PR #412 for route caching."
                )
            elif curr_date == datetime.date(2026, 11, 19):
                act_type = "RESIGNATION_NOTICE"
                summary = "Submitted formal resignation letter to Vikram Menon and Deepa Joshi (60-day notice)"
                details = (
                    "Submitted formal resignation letter citing persistent overwork and lack of backend backfills. "
                    "Notice period is 60 days, scheduled exit date: 2027-01-19. Began drafting Atlas core handoff document."
                )
            else:
                act_type = "ARCHITECTURE_HANDOVER"
                days_left = (datetime.date(2027, 1, 19) - curr_date).days
                summary = f"Notice Period Day {day_num - 18}: Drafting Atlas routing mathematical model documentation ({days_left} days remaining)"
                details = (
                    f"Documenting dynamic partition pruning algorithms. Held 90-minute knowledge transfer session with Rahul Verma "
                    "covering emergency failover switches."
                )

        # === 2. SNEHA KULKARNI (VX012) ===
        elif emp_id == "VX012":
            if day_num % 2 == 0:
                act_type = "INFRA_HANDOVER"
                summary = "Syncing with contractor Patil Infra Services on overnight alert escalations"
                details = (
                    "Reviewed Datadog and PagerDuty alert thresholds with S. Patil. Transferred secondary pager shift "
                    "to Patil Infra to reduce internal alert fatigue."
                )
            else:
                act_type = "SRE_MAINTENANCE"
                summary = "Provisioning read-replicas in AWS RDS Mumbai to prevent routing-api database locks"
                details = (
                    "Optimized Aurora Postgres connection pooling with PgBouncer. Logged zero SEV1 incidents over the past 48 hours."
                )

        # === 3. VIKRAM MENON (VX004) ===
        elif emp_id == "VX004":
            if curr_date >= datetime.date(2026, 11, 19):
                act_type = "EXECUTIVE_CONTINGENCY"
                summary = "Emergency planning session following Priya Nair's resignation: Re-baselining Atlas GA to Q1 2027"
                details = (
                    "Prepared revised engineering roadmap for CEO board call. Formulated proposal to lift hiring freeze on "
                    "REQ-014 and REQ-015 and hire a contract distributed systems specialist."
                )
            else:
                act_type = "JIRA_ROADMAP"
                summary = "Tracking Atlas version 3 burndown in Jira against December 15 milestone"
                details = (
                    "Reviewed sprint velocity across 14 unresolved open issues. Noted frontend blockers on vehicle telemetry view."
                )

        # === 4. RAHUL VERMA (VX018) ===
        elif emp_id == "VX018":
            act_type = "KNOWLEDGE_TRANSFER"
            summary = "Shadowing Priya Nair on routing graph partitioning and Kafka consumer lag"
            details = (
                "Implemented unit tests for latency telemetry ingestion. Attended architecture walkthrough of the data-plane engine."
            )

        # === 5. ARJUN DAS (VX009) ===
        elif emp_id == "VX009":
            act_type = "FRONTEND_DEV"
            summary = "Working remotely from Pune on Atlas client fleet tracking visualizer"
            details = (
                "Completed React component for real-time truck routing maps. Pushed PR #415 for design review with Nikhil."
            )

        # === 6. MEERA IYER (VX003) ===
        elif emp_id == "VX003":
            act_type = "FINANCIAL_MODELING"
            summary = "Monitoring monthly burn rate (Rs. 44.2 Lakhs) against Rs. 6.18 Cr bank balance"
            details = (
                "Modeling cash runway impact of unfreezing REQ-014 backend role vs continuing Patil Infra Services monthly retainer (Rs. 1,41,600)."
            )

        # === 7. KARTHIK SUBRAMANIAN (VX010) ===
        elif emp_id == "VX010":
            act_type = "FP&A_REPORTING"
            summary = "Updating SaaS unit economics: gross margin 72%, Net Revenue Retention at 108%"
            details = (
                "Reconciled AWS infrastructure invoices with Fatima. Completed evening study module for CFA Level II exam."
            )

        # === 8. FATIMA SHEIKH (VX014) ===
        elif emp_id == "VX014":
            act_type = "GL_RECONCILIATION"
            summary = "Processing October vendor invoices in Zoho Books, including Patil Infra Services (PIS-114)"
            details = (
                "Verified TDS and 18% IGST compliance on Invoice PIS-114 (Rs. 1,41,600). Updated WeWork rent payment schedule."
            )

        # === 9. DEEPA JOSHI (VX005) ===
        elif emp_id == "VX005":
            if curr_date >= datetime.date(2026, 11, 19):
                act_type = "RETENTION_INTERVENTION"
                summary = "Exit counseling with Priya Nair and policy pushback against workplace chat surveillance"
                details = (
                    "Drafted proposed retention / advisory package for Priya to document architecture. Reaffirmed strict employee "
                    "privacy standards rejecting private Slack inspection."
                )
            else:
                act_type = "PEOPLE_OPERATIONS"
                summary = "Organizing engineering 1:1 check-ins following Q2 Culture Amp pulse results"
                details = (
                    "Held confidential pulse follow-up with Sneha Kulkarni regarding on-call burnout. Coordinated Diwali holiday leave schedule."
                )

        # === 10. ROHAN BANERJEE (VX015) ===
        elif emp_id == "VX015":
            act_type = "TALENT_ACQUISITION"
            summary = "Engaging Cohere Recruiting Partners regarding pipeline for Senior Backend Engineer (REQ-014)"
            details = (
                "Reviewed 8 candidate profiles for distributed systems roles to utilize the unspent Rs. 1.77L agency advance."
            )

        # === 11. LAKSHMI PILLAI (VX017) ===
        elif emp_id == "VX017":
            act_type = "HR_ADMINISTRATION"
            summary = "Finalizing Siddharth Mehta's exit paperwork and Keka leave balance reconciliations"
            details = (
                "Archived Siddharth's Keka profile following 31 Oct exit. Recorded Priya Nair's 60-day notice period in HRMS."
            )

        # === 12. NIKHIL BOSE (VX006) ===
        elif emp_id == "VX006":
            act_type = "MARKETING_STRATEGY"
            summary = "Aligning with Sales Lead Manoj Kumar on Q3 enterprise pipeline qualification"
            details = (
                "Reviewed feedback on 212 Logistics Summit attendees. Agreed on revised qualification score threshold before routing to sales."
            )

        # === 13. AISHA KHAN (VX011) ===
        elif emp_id == "VX011":
            act_type = "PERFORMANCE_MKTG"
            summary = "Managing Google Ads B2B campaign (~Rs. 85,000 monthly spend) and LinkedIn lead forms"
            details = (
                "Optimized high-intent search keywords for supply-chain routing. Reduced cost-per-lead by 14% week-over-week."
            )

        # === 14. SIDDHARTH MEHTA (VX013) ===
        elif emp_id == "VX013":
            if curr_date <= datetime.date(2026, 10, 31):
                act_type = "NOTICE_HANDOVER"
                summary = "Final day at Veloxa: Handing over Atlas launch kit and customer collateral"
                details = "Completed final exit clearance with Deepa. Handed over Atlas_Launch_Kit_v1.pdf files to Nikhil Bose."
            else:
                act_type = "ALUMNI_STATUS"
                summary = "Departed employee: Relocated for new role (Exit effective 31 Oct 2026)"
                details = (
                    "Siddharth completed his notice period on 31 October 2026. His completed launch kit remains archived with Marketing."
                )
        else:
            act_type = "GENERAL_ACTIVITY"
            summary = f"Standard operational responsibilities in {dept}"
            details = f"Executed day-to-day duties matching {persona['workload_focus']}"

        return {
            "sim_date": date_str,
            "emp_id": emp_id,
            "emp_name": name,
            "dept": dept,
            "activity_type": act_type,
            "summary": summary,
            "details": details,
            "metadata": f"Persona {emp_id} grounded simulation"
        }

    def simulate_day(self, date_str: str) -> List[Dict[str, Any]]:
        """Simulates and persists a full company day across all 14 personas."""
        conn = get_db_connection()
        cur = conn.cursor()
        activities = []

        for emp_id in PERSONA_REGISTRY.keys():
            act = self.generate_persona_activity(emp_id, date_str)
            if not act:
                continue

            cur.execute("""
                INSERT OR REPLACE INTO daily_agent_activities
                (sim_date, emp_id, emp_name, dept, activity_type, summary, details, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                act["sim_date"],
                act["emp_id"],
                act["emp_name"],
                act["dept"],
                act["activity_type"],
                act["summary"],
                act["details"],
                act["metadata"]
            ))
            activities.append(act)

        conn.commit()
        conn.close()
        return activities

    def simulate_range(self, start_date_str: str = "2026-11-01", end_date_str: str = "2026-11-20") -> int:
        """Simulates all consecutive days between start_date and end_date."""
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()

        delta = datetime.timedelta(days=1)
        curr = start_date
        total_days = 0

        while curr <= end_date:
            date_str = curr.strftime("%Y-%m-%d")
            self.simulate_day(date_str)
            total_days += 1
            curr += delta

        return total_days

    def get_daily_digest(self, date_str: str) -> List[Dict[str, Any]]:
        """Retrieves the full company activity digest for a specific simulation date."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT emp_id, emp_name, dept, activity_type, summary, details
            FROM daily_agent_activities
            WHERE sim_date = ?
            ORDER BY dept, emp_id
        """, (date_str,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        # If not populated yet, simulate dynamically
        if not rows:
            self.simulate_day(date_str)
            return self.get_daily_digest(date_str)

        return rows

    def get_agent_timeline(self, emp_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves the chronological activity timeline for an employee."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT sim_date, emp_id, emp_name, dept, activity_type, summary, details
            FROM daily_agent_activities
            WHERE emp_id = ?
            ORDER BY sim_date DESC
            LIMIT ?
        """, (emp_id, limit))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Veloxa Living Persona Simulation (Post-October 2026 Activity)")
    parser.add_argument("--date", "-d", type=str, default="2026-11-19", help="Simulation date (default: 2026-11-19)")
    parser.add_argument("--emp", "-e", type=str, help="Employee ID (e.g. VX007 for Priya Nair)")
    parser.add_argument("--populate", "-p", action="store_true", help="Populate simulation database from 2026-11-01 to 2026-11-20")

    args = parser.parse_args()
    engine = LivingPersonaSimulation()

    if args.populate:
        print("[SIMULATION] Populating daily activities from 2026-11-01 to 2026-11-20...")
        days = engine.simulate_range("2026-11-01", "2026-11-20")
        print(f"[SIMULATION] Successfully simulated and stored {days} days of post-October company activity.\n")

    if args.emp:
        timeline = engine.get_agent_timeline(args.emp)
        if not timeline:
            # Populate if empty
            engine.simulate_range("2026-11-01", "2026-11-20")
            timeline = engine.get_agent_timeline(args.emp)

        print("\n" + "=" * 75)
        print(f" PERSONA ACTIVITY TIMELINE: {args.emp}")
        print("=" * 75)
        for act in timeline:
            print(f"\n[{act['sim_date']}] [{act['activity_type']}] {act['emp_name']} ({act['dept']})")
            print(f"  Summary: {act['summary']}")
            print(f"  Details: {act['details']}")
        print("=" * 75 + "\n")
        return

    # Default: Show daily digest
    digest = engine.get_daily_digest(args.date)
    print("\n" + "=" * 75)
    print(f" VELOXA TECHNOLOGIES — DAILY COMPANY ACTIVITY DIGEST")
    print(f" Simulated Date: {args.date} (Post-October Living Persona Simulation)")
    print("=" * 75)

    by_dept = {}
    for act in digest:
        by_dept.setdefault(act["dept"], []).append(act)

    for dept, acts in by_dept.items():
        print(f"\n>>> {dept.upper()} ({len(acts)}) <<<")
        for a in acts:
            print(f"  • [{a['emp_id']}] {a['emp_name']:<20} | [{a['activity_type']}]")
            print(f"      {a['summary']}")

    print("\n" + "=" * 75)
    print(" Candidate Brief Stretch Goal: 'Agents that keep living after 31 Oct 2026'")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
