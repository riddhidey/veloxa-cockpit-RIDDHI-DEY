# Veloxa CXO Cockpit

An evidence-grounded executive intelligence cockpit and persona simulation system built for **Ananya Rao**, CEO of Veloxa Technologies, for the Hiyaku Systems Hackathon.

---

## What This Project Is

Veloxa Technologies is an early-stage B2B SaaS startup. Its executive leadership relies on disjointed data exports (HRMS Keka, Zoho Books GL, payroll records, board updates, email threads) and noisy speech-to-text transcripts of executive calls.

The **Veloxa CXO Cockpit** solves this by providing:
1. **Fact-Grounded Cockpit Q&A:** Answers CEO queries with verifiable citations to source documents and rows, an explicit confidence rating, and principled refusal or contradiction alerts.
2. **"What Should I Worry About?" View:** A synthesized, evidence-backed list of organizational, financial, and delivery risks.
3. **14 Interactive Employee Persona Agents:** Grounded simulations of 14 employees across Engineering, Finance, People & Ops, and Marketing.
4. **Temporal Point-in-Time Isolation:** Strict time gating so answers reflect only what was known up to a specific date.

---

## One-Command Setup

Run the following command from the repository root to install dependencies, ingest Day 1 data, build the local SQLite database, and launch the cockpit:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ingest Day 1 data and initialize database
python -m src.ingest_day1

# 3. View the CEO "What should I worry about?" radar
python -m src.cockpit --worry
```

---

## Running the Automated Test Suite

Run the full automated test suite using `pytest`:

```bash
pytest tests/
```

Or via Python's built-in `unittest`:

```bash
python -m unittest discover tests
```

---

## Project Structure

```
veloxa-cockpit-[name]/
├── ARCHITECTURE.md          # Complete system architecture and data model
├── ASSUMPTIONS.md           # Log of all persona and domain assumptions
├── TRANSCRIPT_NOTES.md      # ASR phonetic errors and cross-source contradictions
├── DECISIONS.md             # Defensible design and engineering decisions
├── AI_LOG.md                # Record of AI usage, mistakes caught, and human edits
├── README.md                # Project overview and setup instructions
├── requirements.txt         # Python dependencies
├── data/                    # Data room exports and transcripts (Day 1..4)
│   └── day1/
│       ├── brief/           # Candidate brief
│       ├── data_room/       # HR, Finance, Emails, Board updates
│       └── transcripts/     # T1 (CEO kickoff), T2 (CFO call)
├── src/                     # Source code
│   ├── ingest_day1.py       # Day 1 ingestion parser & SQLite builder
│   ├── reconcile.py         # Entity resolution & conflict detection
│   ├── agents.py            # 14 grounded employee persona agents
│   └── cockpit.py           # CXO Q&A engine & worry radar CLI
└── tests/                   # Automated test suite
    └── test_cockpit_day1.py # Test questions and refusal checks
```

---

## Governance & Integrity Logs

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture, data flow, agent design.
- [ASSUMPTIONS.md](ASSUMPTIONS.md) - Assumption log with confidence and invalidation criteria.
- [TRANSCRIPT_NOTES.md](TRANSCRIPT_NOTES.md) - Speech-to-text mishearings and source contradictions.
- [DECISIONS.md](DECISIONS.md) - Technical trade-offs and rationale.
- [AI_LOG.md](AI_LOG.md) - AI collaboration audit trail.
