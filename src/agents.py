"""
14 Grounded Employee Persona Agents for Veloxa CXO Cockpit.
Each agent is grounded in primary HRMS and payroll records, with personal life,
workload, and private thoughts logged in ASSUMPTIONS.md.
"""

import sqlite3
from typing import Dict, List, Optional, Any

DB_PATH = "veloxa.db"

# Master definitions of the 14 grounded personas across Eng, Finance, HR, Marketing
PERSONA_REGISTRY = {
    # === ENGINEERING (5) ===
    "VX004": {
        "emp_id": "VX004",
        "name": "Vikram Menon",
        "dept": "Engineering",
        "title": "VP Engineering",
        "manager_id": "VX001",
        "location": "Bengaluru",
        "join_date": "2021-02-01",
        "personal_life": "Lives in Indiranagar; avid road cyclist and filter coffee snob. Married with an 8-year-old daughter.",
        "workload_focus": "Managing engineering delivery, firefighting Atlas release delays, and balancing technical debt with executive promises.",
        "private_thoughts": (
            "Ananya promises customer release dates before we even finish core architecture. Atlas v3 is solid now, "
            "but August was a nightmare because of database lock contention. We had to bring in Patil Infra to keep the lights on."
        ),
        "assumption_id": "A-011"
    },
    "VX007": {
        "emp_id": "VX007",
        "name": "Priya Nair",
        "dept": "Engineering",
        "title": "Staff Engineer",
        "manager_id": "VX004",
        "location": "Bengaluru",
        "join_date": "2022-03-14",
        "personal_life": "Classical Carnatic vocalist and synthesizer enthusiast. Lives near Koramangala with two rescue cats.",
        "workload_focus": "Lead architect and single point of failure for Atlas routing engine v3 algorithms.",
        "private_thoughts": (
            "Everyone assumes I can magically fix latency spikes. Rahul is smart and eager, but he's too junior to touch "
            "the core routing graph yet. I am terrified of going on vacation because the pager will explode."
        ),
        "assumption_id": "A-012"
    },
    "VX009": {
        "emp_id": "VX009",
        "name": "Arjun Das",
        "dept": "Engineering",
        "title": "Senior Frontend Engineer",
        "manager_id": "VX004",
        "location": "Pune (remote)",
        "join_date": "2023-05-08",
        "personal_life": "Works remotely from Pune; board games collector, amateur baker, active in local open-source meetups.",
        "workload_focus": "Dashboard UI redesign, real-time vehicle tracking visualization for Atlas client portals.",
        "private_thoughts": (
            "Being remote in Pune means I miss hallway decisions. Marketing keeps changing UI copy without updating the design system."
        ),
        "assumption_id": "A-013"
    },
    "VX012": {
        "emp_id": "VX012",
        "name": "Sneha Kulkarni",
        "dept": "Engineering",
        "title": "Site Reliability Engineer",
        "manager_id": "VX004",
        "location": "Bengaluru",
        "join_date": "2024-11-04",
        "personal_life": "Avid trekker in the Western Ghats; marathon runner; keeps detailed personal Notion logs of sleep and fitness.",
        "workload_focus": "AWS infrastructure, Kubernetes cluster stability, PagerDuty alerting, reducing alert fatigue.",
        "private_thoughts": (
            "August broke me. I was on-call for 14 straight nights before Vikram finally approved external help from Patil Infra. "
            "AWS costs are climbing because we over-provisioned RDS instances to prevent crashes."
        ),
        "assumption_id": "A-014"
    },
    "VX018": {
        "emp_id": "VX018",
        "name": "Rahul Verma",
        "dept": "Engineering",
        "title": "Backend Engineer",
        "manager_id": "VX004",
        "location": "Bengaluru",
        "join_date": "2026-02-03",
        "personal_life": "Fresh graduate from NIT Trichy; stays in a PG in HSR Layout; passionate gamer and keyboard modder.",
        "workload_focus": "API service optimization, Kafka consumers for location telemetry under Priya's mentorship.",
        "private_thoughts": (
            "I joined on Feb 3rd and was shocked to get a full month's salary in February. I emailed Fatima honestly to ask if "
            "it was an error, but nobody deducted it in March. I don't want to get into trouble later."
        ),
        "assumption_id": "A-015"
    },

    # === FINANCE (3) ===
    "VX003": {
        "emp_id": "VX003",
        "name": "Meera Iyer",
        "dept": "Finance",
        "title": "CFO",
        "manager_id": "VX001",
        "location": "Bengaluru",
        "join_date": "2023-06-12",
        "personal_life": "Former Big 4 auditor; plays badminton on weekends; classical book club member.",
        "workload_focus": "Cash runway management, board reporting, investor relations, preparing for Series A extension.",
        "private_thoughts": (
            "Ananya has zero financial discipline—she still thinks burn is 2.2 Lakhs when our monthly payroll alone is 31.75 Lakhs! "
            "If the funding round slips past December, we will be forced into an immediate hiring freeze."
        ),
        "assumption_id": "A-016"
    },
    "VX010": {
        "emp_id": "VX010",
        "name": "Karthik Subramanian",
        "dept": "Finance",
        "title": "FP&A Manager",
        "manager_id": "VX003",
        "location": "Bengaluru",
        "join_date": "2024-10-01",
        "personal_life": "Preparing for CFA Level II exam; lives with roommates in BTM Layout; cricket analytics enthusiast.",
        "workload_focus": "Financial modeling, budget vs actual variance analysis, SaaS metric tracking.",
        "private_thoughts": (
            "Balancing 12-hour workdays with CFA prep is killing me. I messed up the February payroll run when Fatima was away "
            "getting married—I just copied the template and paid the new guy Rahul for the whole month."
        ),
        "assumption_id": "A-017"
    },
    "VX014": {
        "emp_id": "VX014",
        "name": "Fatima Sheikh",
        "dept": "Finance",
        "title": "Accounts & Payroll Executive",
        "manager_id": "VX003",
        "location": "Bengaluru",
        "join_date": "2025-05-12",
        "personal_life": "Recently married in February 2026; food blogger specializing in Hyderabadi cuisine; plant parent.",
        "workload_focus": "Vendor invoices, Zoho Books reconciliations, monthly payroll processing, WeWork rent payments.",
        "private_thoughts": (
            "I came back from my wedding leave to find Karthik had made a mess of February payroll. Rahul Verma even flagged his "
            "own overpayment, but Meera told me to hold off manual adjustments until the new quarter."
        ),
        "assumption_id": "A-018"
    },

    # === PEOPLE & OPERATIONS (3) ===
    "VX005": {
        "emp_id": "VX005",
        "name": "Deepa Joshi",
        "dept": "People & Ops",
        "title": "Head of People & Ops",
        "manager_id": "VX001",
        "location": "Bengaluru",
        "join_date": "2022-07-04",
        "personal_life": "Certified yoga instructor; pottery enthusiast; mother of two golden retrievers.",
        "workload_focus": "Organizational culture, hiring strategy, retention programs, office vendor management.",
        "private_thoughts": (
            "Ananya thinks our attrition is alarming, but for an early-stage B2B SaaS in Bangalore, 15% is completely healthy. "
            "What worries me more is engineering burnout and Siddharth leaving marketing."
        ),
        "assumption_id": "A-019"
    },
    "VX015": {
        "emp_id": "VX015",
        "name": "Rohan Banerjee",
        "dept": "People & Ops",
        "title": "Talent Partner",
        "manager_id": "VX005",
        "location": "Kolkata (remote)",
        "join_date": "2024-06-03",
        "personal_life": "Working remotely from Kolkata; documentary film lover; passionate about Bengali theater and vinyl records.",
        "workload_focus": "Technical recruiting for backend engineering roles, managing external search agency Cohere.",
        "private_thoughts": (
            "We paid Cohere Recruiting a 50% advance (1.77L) to find two backend engineers in June, but hiring got frozen right after. "
            "Now that money is stuck with the agency."
        ),
        "assumption_id": "A-020"
    },
    "VX017": {
        "emp_id": "VX017",
        "name": "Lakshmi Pillai",
        "dept": "People & Ops",
        "title": "HR & Office Executive",
        "manager_id": "VX005",
        "location": "Bengaluru",
        "join_date": "2025-10-06",
        "personal_life": "Passionate baker; loves hosting board game nights; active volunteering at animal shelters.",
        "workload_focus": "Onboarding new joiners, Keka HRMS record upkeep, WeWork facility coordination.",
        "private_thoughts": (
            "I'm keeping Keka up to date, but half the time managers make hiring promises without giving me offer letters. "
            "Siddharth's exit clearance for Oct 31 is my main task right now."
        ),
        "assumption_id": "A-021"
    },

    # === MARKETING (3) ===
    "VX006": {
        "emp_id": "VX006",
        "name": "Nikhil Bose",
        "dept": "Marketing",
        "title": "Head of Marketing",
        "manager_id": "VX001",
        "location": "Bengaluru",
        "join_date": "2024-09-02",
        "personal_life": "Former brand agency director; amateur mixologist; podcast host on tech marketing trends.",
        "workload_focus": "Brand positioning, enterprise demand generation, orchestrating the annual Logistics Summit.",
        "private_thoughts": (
            "Meera keeps complaining that my marketing budget numbers don't match hers. The September Logistics Summit was an "
            "unqualified success with 212 registrations, even if we spent 10 Lakhs with Sapphire Events."
        ),
        "assumption_id": "A-022"
    },
    "VX011": {
        "emp_id": "VX011",
        "name": "Aisha Khan",
        "dept": "Marketing",
        "title": "Performance Marketing Manager",
        "manager_id": "VX006",
        "location": "Bengaluru",
        "join_date": "2023-08-21",
        "personal_life": "Latin dance enthusiast; avid traveler across Southeast Asia; amateur specialty coffee roaster.",
        "workload_focus": "Google Ads campaigns, LinkedIn paid acquisition, conversion rate optimization, pipeline attribution.",
        "private_thoughts": (
            "We spend ~80k-90k every month on Google Ads. Our cost-per-lead spiked in August because all enterprise logistics "
            "decision-makers were preparing for Q3 budgets."
        ),
        "assumption_id": "A-023"
    },
    "VX013": {
        "emp_id": "VX013",
        "name": "Siddharth Mehta",
        "dept": "Marketing",
        "title": "Product Marketing Manager",
        "manager_id": "VX006",
        "location": "Bengaluru",
        "join_date": "2025-04-07",
        "status": "Notice period",
        "exit_date": "2026-10-31",
        "personal_life": "Standup comedy open-micer; scuba certified; preparing to relocate for his next career chapter.",
        "workload_focus": "Atlas product messaging, customer case studies, completing transition documentation before Oct 31 exit.",
        "private_thoughts": (
            "I resigned because product deadlines kept slipping and sales kept blaming product marketing for lack of collateral. "
            "My notice period ends 31 Oct 2026, and I'm just wrapping up handovers."
        ),
        "assumption_id": "A-024"
    }
}


class EmployeeAgent:
    def __init__(self, emp_id: str, db_path: str = DB_PATH):
        if emp_id not in PERSONA_REGISTRY:
            raise ValueError(f"Unknown persona agent emp_id: {emp_id}")
        self.data = PERSONA_REGISTRY[emp_id].copy()
        self.emp_id = emp_id
        self.db_path = db_path
        self._load_db_facts()

    def _load_db_facts(self):
        """Loads live salary and status from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Load HR details
        cur.execute("SELECT title, department, manager_id, join_date, status, exit_date FROM employees WHERE emp_id = ?", (self.emp_id,))
        row = cur.fetchone()
        if row:
            self.data["title"] = row[0]
            self.data["dept"] = row[1]
            self.data["manager_id"] = row[2]
            self.data["join_date"] = row[3]
            self.data["status"] = row[4]
            self.data["exit_date"] = row[5]

        # Load latest payroll gross
        cur.execute("SELECT gross, net, month FROM payroll_records WHERE emp_id = ? ORDER BY id DESC LIMIT 1", (self.emp_id,))
        p_row = cur.fetchone()
        if p_row:
            self.data["latest_gross"] = p_row[0]
            self.data["latest_net"] = p_row[1]
            self.data["payroll_month"] = p_row[2]

        conn.close()

    def get_grounded_profile(self) -> Dict[str, Any]:
        """Returns the full grounded profile combining facts and assumptions."""
        return self.data

    def interview(self, question: str) -> Dict[str, Any]:
        """
        Interviews the agent. The agent responds in character, strictly adhering
        to their grounded facts, department perspective, and private context.
        """
        q_lower = question.lower()
        name = self.data["name"]
        title = self.data["title"]
        dept = self.data["dept"]

        # 1. Specialized persona topics (checked first for persona-specific depth)
        if self.emp_id == "VX018" and any(w in q_lower for w in ["payroll", "february", "first pay", "overpay", "payslip"]):
            response = (
                "When I joined on Feb 3, 2026, my first payslip had 28 days of full pay. I reached out to Fatima "
                "in accounting (email on March 6) because it looked high for a partial month. She said she'd check, "
                "but I haven't heard back."
            )
            citation = "Email 02.eml & Payroll_Register_Jan-Mar_2026.xlsx: VX018"

        elif self.emp_id == "VX007" and any(w in q_lower for w in ["late night", "ownership", "09.eml", "talk to vikram"]):
            response = (
                "On September 1 at 11:47 PM, I sent an email to Vikram (09.eml) requesting time to discuss Atlas ownership. "
                "I was exhausted from firefighting alone while being expected to single-handedly build real-time re-routing."
            )
            citation = "Email 09.eml & T5 VP Engineering Call"

        elif self.emp_id == "VX007" and any(w in q_lower for w in ["atlas", "routing", "delay", "status", "v3"]):
            response = (
                "Atlas routing engine v3 is feature complete, but reliability under high load has been brutal. "
                "We had database contention in August that forced us to bring in Patil Infra for on-call relief. "
                "I am working on stabilizing real-time re-routing."
            )
            citation = "Board_Update_Jul-Sep_2026.pdf & GL_Export_Apr-Sep_2026.xlsx (JV-0902)"

        elif self.emp_id == "VX003" and any(w in q_lower for w in ["burn", "cash", "runway"]):
            response = (
                "Our monthly burn rate is approximately Rs. 44 Lakhs to 46 Lakhs, with runway at roughly 13-14 months. "
                "Payroll alone is Rs. 31.75 Lakhs monthly. If our funding round slips, we must freeze hiring immediately."
            )
            citation = "Board_Update_Jul-Sep_2026.pdf & GL_Export_Apr-Sep_2026.xlsx"

        elif self.emp_id == "VX013" and any(w in q_lower for w in ["leaving", "notice", "exit", "resigned"]):
            response = (
                f"Yes, I submitted my resignation and my notice period ends on {self.data.get('exit_date', '2026-10-31')}. "
                "I am finishing up my documentation for the Atlas product marketing handover."
            )
            citation = "Employee_Master.xlsx: VX013"

        elif self.emp_id == "VX010" and any(w in q_lower for w in ["cfa", "forecast", "february payroll", "wedding"]):
            response = (
                "I was covering payroll in February while Fatima was away for her wedding. Between that and studying "
                "for my CFA exams, things were intense. I used the previous month's template and added the new joiners."
            )
            citation = "Email 01.eml & T2 CFO Call"

        # === Day 2 Persona Grounding Topics ===
        elif self.emp_id == "VX007" and any(w in q_lower for w in ["leave", "september", "interview", "afternoon", "half day", "flight risk"]):
            response = (
                "I took five half-day personal leaves in September for private personal commitments. "
                "I have been carrying the Atlas routing engine completely alone, and when the two backend reqs were "
                "frozen in August, I felt completely unsupported."
            )
            citation = "Leave_Register.xlsx (P. Nair: Sep 2026) & ASSUMPTIONS.md [A-025]"

        elif self.emp_id == "VX005" and any(w in q_lower for w in ["worried engineer", "pulse", "engagement", "survey", "attrition"]):
            response = (
                "Our engineering pulse score dropped sharply to 3.1 in Q2. Priya is carrying too much load alone, "
                "and her multiple half-day leaves in September are an undeniable flight risk signal. "
                "I flagged this directly to Ananya in my email on Sept 29."
            )
            citation = "Email 11.eml, Pulse_Survey.xlsx & T3 Head of People Call"

        elif self.emp_id == "VX015" and any(w in q_lower for w in ["22 roles", "twenty-two", "open roles", "cohere", "req-014", "hiring freeze"]):
            response = (
                "Leadership spoke about 22 roles on their wishlist, but only 6 formal reqs existed in Keka. "
                "We had strong finalists for the two backend engineer roles, but Meera froze REQ-014 and REQ-015 "
                "on August 12 to prioritize cash burn, leaving our 1.77L advance with Cohere unused."
            )
            citation = "Hiring_Tracker.xlsx & Email 06.eml"

        elif self.emp_id == "VX009" and any(w in q_lower for w in ["pune", "remote", "permanent", "bangalore"]):
            response = (
                "I moved to Pune in March and sent an email to Deepa on Sept 18 asking to make my remote arrangement "
                "permanent. I am happy to travel to Bengaluru once a month for key sprints."
            )
            citation = "Email 10.eml & Leave_Register.xlsx"

        elif self.emp_id == "VX013" and any(w in q_lower for w in ["why did you leave", "why resign", "reason", "resignation letter", "launch timelines", "leaving", "leave", "resigned", "exit"]):
            response = (
                "As I stated in my resignation letter to Nikhil on Sept 15, I decided to leave because of continuous "
                "launch delays. I want to work in an environment with predictable roadmaps where my launch collateral reaches customers."
            )
            citation = "Resignation_Letter_SM.pdf"

        elif self.emp_id == "VX004" and any(w in q_lower for w in ["freeze", "absorb", "backend reqs", "req-014", "req-015"]):
            response = (
                "When Meera emailed me on August 12 to pause REQ-014 and REQ-015 for cash burn, I replied that we would absorb it. "
                "In hindsight, freezing those roles right before the August database crisis forced Priya into burnout."
            )
            citation = "Email 06.eml & Email 07.eml"

        # === Day 3 Persona Grounding Topics ===
        elif self.emp_id == "VX012" and any(w in q_lower for w in ["on-call", "oncall", "rota", "outage", "sev1", "patil", "burnout", "incident"]):
            response = (
                "August broke me. We had three SEV1 outages on routing-api (INC-201, INC-203, INC-205). "
                "I was scheduled as both primary and secondary on-call week after week under 'Sneha' and 'Snehal' until I emailed "
                "Vikram on Aug 24 (08.eml) to pause Atlas performance tickets. We had to hire Patil Infra Services on a monthly "
                "retainer (Invoice PIS-114: Rs. 1.41L) just to keep on-call covered."
            )
            citation = "Incidents_Aug-Oct_2026.xlsx, OnCall_Rota.xlsx, Email 08.eml & Invoice_PIS-114.pdf"

        elif self.emp_id == "VX004" and any(w in q_lower for w in ["december", "december 15", "jira date", "buffer", "september-ish", "deception", "delay"]):
            response = (
                "On September 2, I officially changed the Atlas GA release date in Jira to 15 December 2026 after Priya's "
                "urgent late-night email (09.eml) and the August reliability outages. When I spoke to Ananya on call T5, "
                "I described it as 'September-ish with buffer' to avoid causing panic before our board milestones."
            )
            citation = "Jira_Export_ATLAS.xlsx (Versions sheet), Email 09.eml & T5 Call"

        elif self.emp_id == "VX007" and any(w in q_lower for w in ["late night", "ownership", "09.eml", "talk to vikram"]):
            response = (
                "On September 1 at 11:47 PM, I sent an email to Vikram (09.eml) requesting time to discuss Atlas ownership. "
                "I was exhausted from firefighting alone while being expected to single-handedly build real-time re-routing."
            )
            citation = "Email 09.eml & T5 VP Engineering Call"

        elif self.emp_id == "VX013" and any(w in q_lower for w in ["launch kit", "collateral", "july", "deck", "ready"]):
            response = (
                "I finished the entire Atlas v1 launch kit back on 21 July (Atlas_Launch_Kit_v1.pdf), including the sales deck, "
                "draft website page, and 3 customer emails. I emailed Nikhil on 22 July (05.eml) saying everything was ready "
                "and we just needed a release date from engineering. It sat untouched for months."
            )
            citation = "Atlas_Launch_Kit_v1.pdf & Email 05.eml"

        elif self.emp_id == "VX006" and any(w in q_lower for w in ["cro", "reporting", "cold leads", "manoj", "sales"]):
            response = (
                "Manoj claims our summit leads were cold, but we delivered 212 registrations. Regarding Ananya's voice note "
                "about marketing reporting into a new CRO—nobody has discussed this with me or introduced any candidate. "
                "Re-organizing marketing under an unannounced hire right when Sid is exiting creates unnecessary instability."
            )
            citation = "T4 Head of Marketing Call & T6b CEO Voice Note"

        elif self.emp_id == "VX011" and any(w in q_lower for w in ["google ads", "linkedin", "campaign", "search"]):
            response = (
                "I run our Google Ads campaigns (~Rs. 80k-90k/month) and LinkedIn brand campaigns. Paid search drives solid inbound "
                "traffic, but attributing pipeline from events like the Summit requires closer alignment with sales."
            )
            citation = "T4 Call & GL_Export_Apr-Sep_2026.xlsx"

        # === Day 4 Persona Grounding Topics ===
        elif self.emp_id == "VX007" and any(w in q_lower for w in ["resign", "resigned", "resignation", "notice period", "quit", "leaving"]):
            response = (
                "I formally submitted my resignation on the morning of 19 November 2026. My notice period is 60 days (two months), "
                "putting my final departure in mid-January 2027. I have been shouldering 80%+ of the Atlas routing codebase completely alone "
                "while leadership froze the promised backend backfills in August. I can no longer sacrifice my health for impossible schedules."
            )
            citation = "T6d CEO Voice Note, Employee_Master.xlsx: VX007 & git_log.csv"

        elif self.emp_id == "VX005" and any(w in q_lower for w in ["slag", "slack", "surveillance", "spy", "spying", "reading messages", "did you say"]):
            response = (
                "I never told Ananya that reading employees' private Slack messages is fine. As Head of People, workplace surveillance "
                "violates employee trust and basic labor ethics. We gauge sentiment through anonymous pulse surveys and open 1:1s, "
                "not covert chat snooping."
            )
            citation = "T6c CEO Voice Note, T3 Call & People Ops Policy Framework"

        elif self.emp_id == "VX004" and any(w in q_lower for w in ["priya resign", "priya's resign", "priya resigned", "priya resignation", "board", "version 3 impact", "version three impact"]):
            response = (
                "Priya's resignation this morning is an absolute disaster for Atlas GA. She built the routing mathematics from scratch. "
                "With REQ-014 and REQ-015 frozen since August, nobody on our team can step in. I have to tell Ananya that Dec 15 is off the table "
                "and we need to re-baseline for Q1 2027 while hiring emergency senior contractors."
            )
            citation = "T6d CEO Voice Note, git_log.csv & Jira_Export_ATLAS.xlsx"

        # 2. Questions about role / duties
        elif any(w in q_lower for w in ["what do you do", "role", "responsibilities", "job"]):
            response = f"I am {name}, {title} in {dept}. My main focus is {self.data['workload_focus']}"
            citation = f"Employee_Master.xlsx: {self.emp_id}"

        # 3. Questions about personal life / outside work
        elif any(w in q_lower for w in ["personal life", "outside work", "hobbies", "weekend", "family"]):
            response = f"Outside of work: {self.data['personal_life']}"
            citation = f"ASSUMPTIONS.md: [{self.data['assumption_id']}]"

        # 4. Questions about private thoughts / what's actually happening
        elif any(w in q_lower for w in ["honest", "actually think", "private", "worry", "frustrated", "secret"]):
            response = f"{self.data['private_thoughts']}"
            citation = f"ASSUMPTIONS.md: [{self.data['assumption_id']}] & Internal Context"

        # 5. Questions about compensation / salary
        elif any(w in q_lower for w in ["salary", "pay", "compensation", "gross"]):
            gross = self.data.get("latest_gross", "undisclosed")
            month = self.data.get("payroll_month", "recent")
            response = f"As of {month}, my recorded gross monthly salary is Rs. {gross:,.0f}."
            citation = f"Payroll_Register_Jan-Mar_2026.xlsx: {self.emp_id}"

        # Default fallback
        else:
            response = (
                f"Speaking as {title} in {dept}: {self.data['workload_focus']}. "
                f"Regarding your question, I focus on my day-to-day responsibilities at Veloxa."
            )
            citation = f"Employee_Master.xlsx: {self.emp_id}"

        return {
            "agent_id": self.emp_id,
            "agent_name": name,
            "title": title,
            "department": dept,
            "question": question,
            "response": response,
            "citation": citation,
            "confidence": "HIGH"
        }


def get_all_14_agents() -> List[EmployeeAgent]:
    """Returns initialized list of all 14 grounded employee persona agents."""
    return [EmployeeAgent(emp_id) for emp_id in sorted(PERSONA_REGISTRY.keys())]


def main():
    print("=== Veloxa 14 Grounded Employee Persona Agents ===")
    agents = get_all_14_agents()
    print(f"Loaded {len(agents)} personas across Engineering, Finance, People & Ops, Marketing:\n")
    
    for ag in agents:
        p = ag.get_grounded_profile()
        print(f"• [{p['emp_id']}] {p['name']} | {p['title']} ({p['dept']}) | Location: {p['location']}")

    # Sample interview
    print("\n--- Sample Interview: Priya Nair (Staff Engineer, VX007) ---")
    priya = EmployeeAgent("VX007")
    res1 = priya.interview("What is the status of Atlas and why was it delayed?")
    print(f"Q: {res1['question']}")
    print(f"A: {res1['response']}")
    print(f"Citation: {res1['citation']}")

    print("\n--- Sample Interview: Rahul Verma (Backend Engineer, VX018) ---")
    rahul = EmployeeAgent("VX018")
    res2 = rahul.interview("Did you notice any problem with your first payroll?")
    print(f"Q: {res2['question']}")
    print(f"A: {res2['response']}")
    print(f"Citation: {res2['citation']}")


if __name__ == "__main__":
    main()
